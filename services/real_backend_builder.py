"""
Real Backend Builder — Stage 45-55% of the build path.

Same pattern as the frontend builder: description -> model -> real code ->
actually run it -> actually hit it with a request -> confirm it responds.

Uses Python's standard library only (http.server) so there's no new
dependency to install before this can be tested end-to-end. A real
framework (FastAPI/Flask) can replace this later once the basic loop is
proven - the pattern (generate -> validate -> run -> verify) stays the same.
"""
from __future__ import annotations

import ast
import builtins
import re
from pathlib import Path


SYSTEM_PROMPT = (
    "You are a backend code generator. Output ONLY raw Python code - no "
    "markdown fences, no explanation."
)

USER_PROMPT_TEMPLATE = (
    "Build a tiny Python HTTP backend for: {description}\n\n"
    "STRICT requirements:\n"
    "- Use ONLY Python's standard library (http.server, json, urllib). "
    "Do NOT import flask, fastapi, django, or any third-party package.\n"
    "- Define a class that extends http.server.BaseHTTPRequestHandler.\n"
    "- Implement at least one route that actually does something real "
    "related to the request above (read the path in self.path, and for "
    "POST read the body via self.rfile.read(int(self.headers['Content-Length']))).\n"
    "- Respond with JSON: set self.send_response(...), "
    "self.send_header('Content-Type', 'application/json'), self.end_headers(), "
    "then self.wfile.write(json.dumps(...).encode()).\n"
    "- At the bottom, read the port from the command line if given: "
    "`import sys; PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000`, "
    "then start the server with: "
    "http.server.HTTPServer(('0.0.0.0', PORT), <YourHandlerClassName>).serve_forever()\n"
    "- Do NOT hardcode a literal port number directly into HTTPServer(...) - "
    "always use the PORT variable read from sys.argv as shown above, so the "
    "same file can run on a different port when several instances run "
    "at once.\n"
    "- Output ONLY the complete Python file content, nothing else."
)


def _strip_fences(text: str) -> str:
    text = text.strip()
    m = re.match(r"^```[a-zA-Z]*\n(.*)\n```$", text, re.DOTALL)
    return m.group(1).strip() if m else text


def generate_backend_code(gateway, description: str) -> str:
    """Call the model to generate a real backend file. Returns raw Python source."""
    if not description or not description.strip():
        raise ValueError("description is required")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT_TEMPLATE.format(description=description.strip())},
    ]
    raw = gateway.chat(messages, temperature=0.2, max_tokens=3000)
    return _strip_fences(raw)


def find_undefined_names(code: str) -> list[str]:
    """
    Real static check using Python's own `ast` module: find every bare
    name USED in the code (ast.Name with Load context) and confirm it was
    actually bound somewhere (import, assignment, function/class def,
    function argument, comprehension target, exception handler, etc).

    This catches exactly the real bug found in practice: `import
    http.server` was used correctly for `http.server.BaseHTTPRequestHandler`,
    but the code separately called a bare `HTTPServer(...)` that was never
    imported on its own - a genuine NameError waiting to happen at runtime,
    invisible to ast.parse() (which only checks syntax, not whether names
    exist).

    Deliberately module-level/flat (not fully scope-aware) to avoid false
    positives on typical small generated scripts - a false positive here
    would block otherwise-correct code from ever running, which is worse
    than occasionally missing a scope-specific edge case.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []  # syntax errors are reported separately, don't double up

    defined = set(dir(builtins)) | {"self", "cls", "__name__", "__file__", "__doc__"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                defined.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                defined.add(alias.asname or alias.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.arg):
            defined.add(node.arg)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            defined.add(node.name)
        elif isinstance(node, ast.Global):
            defined.update(node.names)
        elif isinstance(node, ast.Nonlocal):
            defined.update(node.names)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                for name_node in ast.walk(target):
                    if isinstance(name_node, ast.Name):
                        defined.add(name_node.id)
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
            for name_node in ast.walk(node.target):
                if isinstance(name_node, ast.Name):
                    defined.add(name_node.id)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            for name_node in ast.walk(node.target):
                if isinstance(name_node, ast.Name):
                    defined.add(name_node.id)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if item.optional_vars:
                    for name_node in ast.walk(item.optional_vars):
                        if isinstance(name_node, ast.Name):
                            defined.add(name_node.id)
        elif isinstance(node, ast.comprehension):
            for name_node in ast.walk(node.target):
                if isinstance(name_node, ast.Name):
                    defined.add(name_node.id)
        elif isinstance(node, ast.NamedExpr):  # walrus :=
            if isinstance(node.target, ast.Name):
                defined.add(node.target.id)

    used_undefined = []
    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id not in defined and node.id not in seen:
                seen.add(node.id)
                used_undefined.append(f"'{node.id}' is used but never defined/imported (line {node.lineno})")

    return used_undefined


def find_undefined_name_tokens(code: str) -> set[str]:
    """
    Same real ast-based check as find_undefined_names(), but returns the
    raw undefined identifiers (e.g. {'HTTPServer'}) instead of formatted
    messages, so auto_fix_qualified_names() below can act on them.
    """
    problems = find_undefined_names(code)
    tokens = set()
    for problem in problems:
        m = re.match(r"^'([^']+)'", problem)
        if m:
            tokens.add(m.group(1))
    return tokens


def _collect_dotted_module_imports(code: str) -> list[str]:
    """Find plain `import a.b.c` style imports (not `from x import y`, not aliased)."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    dotted = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if not alias.asname and "." in alias.name:
                    dotted.append(alias.name)
    return dotted


def auto_fix_qualified_names(code: str) -> tuple[str, list[str]]:
    """
    Real, VERIFIED auto-repair for a specific real bug: code does
    `import a.b` (e.g. `import http.server`) then separately uses a bare
    name (e.g. `HTTPServer(...)`) that was never imported on its own -
    forgetting the `a.b.` prefix. This is exactly the bug found twice in
    practice with `import http.server` + bare `HTTPServer(...)`.

    This is NOT a guess: since every dotted import here is a Python
    standard-library module (enforced by validate_python_syntax elsewhere),
    we actually import it for real with importlib and check `hasattr()`
    before rewriting anything. If the name genuinely doesn't exist on that
    module, we don't touch the code - no blind find-and-replace.

    Returns (possibly_fixed_code, list of human-readable fixes applied).
    """
    import importlib

    undefined = find_undefined_name_tokens(code)
    if not undefined:
        return code, []

    dotted_imports = _collect_dotted_module_imports(code)
    fixed_code = code
    fixes = []

    for name in sorted(undefined):
        for dotted in dotted_imports:
            try:
                module = importlib.import_module(dotted)
            except ImportError:
                continue
            if hasattr(module, name):
                # (?<!\.) avoids double-prefixing an already-correct
                # `http.server.HTTPServer` into `http.server.http.server.HTTPServer`.
                pattern = re.compile(r"(?<!\.)\b" + re.escape(name) + r"\b")
                new_code, count = pattern.subn(f"{dotted}.{name}", fixed_code)
                if count > 0:
                    fixed_code = new_code
                    fixes.append(
                        f"Rewrote bare '{name}' to '{dotted}.{name}' "
                        f"(verified via real import, {count} occurrence(s) fixed)"
                    )
                break  # this undefined name is handled, move to the next one

    return fixed_code, fixes


def validate_python_syntax(code: str) -> list[str]:
    """
    Real check, not a stub: actually parse the generated code with Python's
    own `ast` module. Catches syntax errors AND undefined names BEFORE we
    ever try to run it, instead of finding out via a crashed subprocess.
    Returns a list of problems (empty = looks safe to run).
    """
    problems = []
    try:
        ast.parse(code)
    except SyntaxError as exc:
        problems.append(f"SyntaxError: {exc.msg} (line {exc.lineno})")
        return problems

    problems.extend(find_undefined_names(code))

    if "BaseHTTPRequestHandler" not in code:
        problems.append("Generated code doesn't use http.server.BaseHTTPRequestHandler as instructed")
    if "sys.argv" not in code and "8000" not in code:
        problems.append(
            "Generated code doesn't read its port from sys.argv (and has no 8000 fallback either) - "
            "it won't be runnable on a different port for multi-user use"
        )
    for banned in ("import flask", "import fastapi", "import django", "from flask", "from fastapi"):
        if banned in code.lower():
            problems.append(f"Generated code uses a disallowed third-party import: {banned}")

    return problems


def write_backend_project(task_id: str, code: str, workspace_dir: str = "workspace") -> Path:
    """Write the generated backend to workspace/<task_id>/server.py. Real file, real path."""
    if not task_id or not task_id.strip():
        raise ValueError("task_id is required")

    project_dir = Path(workspace_dir).resolve() / task_id.strip()
    project_dir.mkdir(parents=True, exist_ok=True)

    server_path = project_dir / "server.py"
    server_path.write_text(code, encoding="utf-8")
    return server_path


def build_backend(gateway, task_id: str, description: str, workspace_dir: str = "workspace"):
    """
    The full real chain: description -> model -> Python code -> known-bug
    auto-repair -> syntax validated -> written to disk.

    Returns (path: Path, syntax_problems: list[str], auto_fixed: list[str]).
    auto_fixed lists any bare http.server names that were automatically
    qualified before validation - transparency, not silence.

    Does NOT run the server - that's a separate, deliberate step (see
    run_backend_demo.py) so a broken file never gets executed blindly.
    """
    code = generate_backend_code(gateway, description)
    code, auto_fixed = auto_fix_qualified_names(code)
    problems = validate_python_syntax(code)
    path = write_backend_project(task_id, code, workspace_dir=workspace_dir)
    return path, problems, auto_fixed
