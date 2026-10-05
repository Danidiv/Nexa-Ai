"""
Real React Builder — the new "React track" of the build path.

Same pattern as real_frontend_builder.py, adapted for React + Vite:
    description -> model generates ONE component (src/App.tsx)
    -> scaffolded into a real Vite project (package.json, vite.config.js,
       index.html, src/main.tsx copied from a working template)
    -> a REAL Vite dev server actually starts
    -> we fetch the REAL compiled module from it - if Vite's own esbuild
       transform fails (bad JSX, syntax error), the dev server returns a
       real 500 with a real error message, which IS our validator. There's
       no Python `ast` equivalent for JSX, so the toolchain itself is used
       as the check, exactly like it would be for a human developer.

TEMPLATE_DIR is a working scaffold (react_scaffold_test/) with node_modules
already installed. Every new project copies the scaffold files and
SYMLINKS node_modules (instead of a slow per-project npm install), since
node_modules only needs to be read, never written, during `vite dev`.
"""
from __future__ import annotations

import re
import shutil
import socket
import subprocess
import threading
import sys
import time
import urllib.request
import urllib.error
import json
from pathlib import Path

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "react_scaffold_test"

SYSTEM_PROMPT = (
    "You are a React component generator. Output ONLY the raw content of "
    "ONE file: src/App.tsx. No markdown fences, no explanation."
)

USER_PROMPT_TEMPLATE = (
    "Build this: {description}\n\n"
    "Requirements:\n"
    "- Export a single default function component named App.\n"
    "- Use Tailwind CSS utility classes for styling (already available, "
    "no import needed) - do NOT write a <style> tag or inline CSS.\n"
    "- Use React hooks (useState, etc.) from 'react' for any interactivity.\n"
    "- Do NOT include <html>, <head>, or <body> tags - this is a component, "
    "not a full page.\n"
    "- You may import these pre-installed shadcn/ui components if useful: "
    "import { Button } from '@/components/ui/button', "
    "import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } "
    "from '@/components/ui/card', "
    "import { Input } from '@/components/ui/input', "
    "import { Label } from '@/components/ui/label', "
    "import { Badge } from '@/components/ui/badge'. "
    "These four/five components are pre-installed; do not invent other local UI paths.\n"
    "- Do NOT import any package other than 'react' and the shadcn "
    "components listed above.\n"
    "- This is a TypeScript file (.tsx) - simple prop/state types are fine, "
    "but don't over-engineer types.\n"
    "- Output ONLY the raw .tsx file content."
)


_VITE_ERROR_JSON_RE = re.compile(r"const error = (\{.*\})\s*\n\s*try \{", re.DOTALL)


def _parse_vite_error_body(body: str) -> str:
    """
    Vite's dev server reports a compile error as a full standalone HTML
    page (an error-overlay document) with the real diagnostic buried in a
    JSON literal inside a <script> tag - not as plain text. Truncating
    that raw HTML with body[:400] mostly just returns boilerplate
    (`<!DOCTYPE html>...`), and if it's ever displayed anywhere
    HTML-aware, an empty `<body></body>` is literally what renders -
    which is exactly what makes the error look blank. Pull out the real
    `message`/`loc` fields and return a short, plain-text summary instead.
    Falls back to the raw (truncated) body if the page doesn't match the
    expected shape, so nothing is ever silently lost.
    """
    m = _VITE_ERROR_JSON_RE.search(body)
    if not m:
        return body[:400]
    try:
        data = json.loads(m.group(1))
    except (json.JSONDecodeError, ValueError):
        return body[:400]
    message = str(data.get("message", "")).strip()
    loc = data.get("loc")
    plugin = data.get("plugin")
    parts = [message[:600]] if message else [body[:400]]
    if loc and isinstance(loc, dict) and "line" in loc:
        parts.append(f"(at line {loc['line']}, column {loc.get('column', '?')})")
    if plugin:
        parts.append(f"[{plugin}]")
    return " ".join(parts)


def _strip_fences(text: str) -> str:
    """
    Pull the code out of a model response.

    The old version only matched when the ENTIRE response was one fenced
    block (``^```...```$``). Small/local models routinely add a leading
    sentence ("Here's the component:") or a trailing note after the
    closing fence, or get cut off by max_tokens before the closing fence
    is ever written - all of which made the old regex fail to match, so
    the raw text (including the un-stripped fences and any commentary)
    was passed straight through as "code".

    This version finds a fenced block ANYWHERE in the text, and falls
    back to stripping just the opening fence when the closing fence is
    missing (a truncated response), instead of giving up.
    """
    text = text.strip()

    # A complete fenced block anywhere in the response.
    m = re.search(r"```[a-zA-Z]*\n(.*?)\n```", text, re.DOTALL)
    if m:
        return m.group(1).strip()

    # An opening fence with no closing fence (truncated generation) -
    # still recover the code that follows it.
    m = re.match(r"^```[a-zA-Z]*\n(.*)$", text, re.DOTALL)
    if m:
        return m.group(1).strip()

    return text


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def ensure_npm_dependency(project_dir: Path, package_name: str, progress=None, timeout: float = 180.0) -> tuple[bool, str]:
    """Install one missing runtime dependency without consuming an LLM repair attempt.

    Generated code can legitimately import a package that is not part of the base
    scaffold. That is a dependency/environment repair, not a reason to ask the
    model to rewrite otherwise-valid code. npm is also allowed to replace the
    shared node_modules symlink with a project-local install when necessary.
    """
    package_name = (package_name or "").strip()
    if not re.fullmatch(r"(?:@[^/\s]+/[^/\s]+|[A-Za-z0-9_.-]+)", package_name):
        return False, f"Invalid npm package name: {package_name!r}"
    npm = shutil.which("npm")
    if npm is None:
        return False, "npm was not found on PATH"
    if progress:
        progress("build", f"Missing dependency detected: {package_name}; installing automatically", package=package_name)
    cmd = [npm, "install", package_name, "--package-lock=false", "--no-audit", "--no-fund", "--ignore-scripts"]
    try:
        result = subprocess.run(
            cmd, cwd=str(project_dir), capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired as exc:
        detail = (str(exc) or "npm install timed out")[-1800:]
        return False, f"npm install {package_name} timed out: {detail}"
    output = ((result.stdout or "") + "\n" + (result.stderr or "")).strip()
    if result.returncode != 0:
        lowered = output.lower()
        invalid_markers = (
            "npm error code e404",
            "404 not found",
            "not found - get https://registry.npmjs.org/",
            "etarget",
            "no matching version found",
            "no matching version",
        )
        if any(marker in lowered for marker in invalid_markers):
            return False, f"INVALID_NPM_PACKAGE: {package_name}: {output[-2200:]}"
        return False, f"npm install {package_name} failed (exit {result.returncode}): {output[-2200:]}"
    if not (project_dir / "node_modules" / package_name).exists():
        return False, f"npm reported success but {package_name!r} is still unavailable"
    if progress:
        progress("build", f"Installed missing dependency: {package_name}", package=package_name)
    return True, output[-2200:]


def missing_dependency_from_vite_error(problem: str) -> str | None:
    """Extract a bare package name from Vite's unresolved-import diagnostic."""
    m = re.search(r'Failed to resolve import ["\']([^"\']+)["\']', problem)
    if not m:
        return None
    name = m.group(1).strip()
    if name.startswith((".", "/", "@/", "#")):
        return None
    # Vite reports subpath imports such as "chart.js/auto". npm needs the
    # package root ("chart.js"), not the import subpath. For scoped packages
    # keep the scope/name pair and strip any deeper export path.
    if name.startswith("@"):
        parts = name.split("/")
        if len(parts) >= 2 and re.fullmatch(r"@[A-Za-z0-9_.-]+", parts[0]) and re.fullmatch(r"[A-Za-z0-9_.-]+", parts[1]):
            return f"{parts[0]}/{parts[1]}"
        return None
    root = name.split("/", 1)[0]
    if re.fullmatch(r"[A-Za-z0-9_.-]+", root):
        return root
    return None


def generate_app_component(gateway, description: str) -> str:
    """Call the model for real. Returns raw JSX source for src/App.tsx."""
    if not description or not description.strip():
        raise ValueError("description is required")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT_TEMPLATE.format(description=description.strip())},
    ]
    raw = gateway.chat(messages, temperature=0.2, max_tokens=3000)
    jsx = _strip_fences(raw)

    if "export default function" not in jsx and "export default" not in jsx:
        raise ValueError("Model did not return a default-exported component. Got:\n" + jsx[:300])
    for banned in ("<html", "<head>", "<body>", "import flask", "import fastapi"):
        if banned in jsx.lower():
            raise ValueError(f"Generated component wrongly includes {banned!r}")
    return jsx


def _node_modules_platform_ready(node_modules: Path) -> bool:
    """Return whether the cached native toolchain matches this runtime platform."""
    if not (node_modules / ".bin" / "vite").exists() or not (node_modules / "react").exists():
        return False
    # Vite/Rollup and esbuild ship platform-native optional packages. A copied
    # Windows cache must never be treated as valid on Linux (or vice versa).
    import platform as _platform
    system = _platform.system().lower()
    machine = _platform.machine().lower()
    if system == "windows" and machine in {"amd64", "x86_64"}:
        expected_rollup = node_modules / "@rollup" / "rollup-win32-x64-gnu"
        expected_esbuild = node_modules / "@esbuild" / "win32-x64"
    elif system == "linux" and machine in {"amd64", "x86_64"}:
        expected_rollup = node_modules / "@rollup" / "rollup-linux-x64-gnu"
        expected_esbuild = node_modules / "@esbuild" / "linux-x64"
    elif system == "darwin" and machine in {"amd64", "x86_64"}:
        expected_rollup = node_modules / "@rollup" / "rollup-darwin-x64"
        expected_esbuild = node_modules / "@esbuild" / "darwin-x64"
    elif system == "darwin" and machine in {"arm64", "aarch64"}:
        expected_rollup = node_modules / "@rollup" / "rollup-darwin-arm64"
        expected_esbuild = node_modules / "@esbuild" / "darwin-arm64"
    else:
        # Unknown platforms fall back to the basic executable check rather
        # than incorrectly rejecting a potentially compatible cache.
        return True
    return expected_rollup.exists() and expected_esbuild.exists()


def scaffold_react_project(task_id: str, workspace_dir: str = "workspace") -> Path:
    """
    Real scaffold: copies the working template's config files (package.json,
    vite.config.js, tsconfig.json, tailwind.config.js, postcss.config.js,
    index.html), the real entry point (src/main.tsx, src/index.css), and
    the pre-installed shadcn/ui foundation (src/lib/utils.ts and every
    src/components/ui/*.tsx component) into a new project dir. Then
    SYMLINKS node_modules from the template (read-only reuse - fast, no
    per-project npm install needed). Real files, real symlink, checked to
    exist.
    """
    if not TEMPLATE_DIR.exists():
        raise RuntimeError(f"React template not found at {TEMPLATE_DIR}")
    # A zipped/deployed template can contain a partial node_modules tree (for
    # example package folders without .bin shims). Treat that as missing and
    # bootstrap it instead of symlinking a broken dependency cache.
    node_modules_ready = _node_modules_platform_ready(TEMPLATE_DIR / "node_modules")
    if not node_modules_ready:
        # Autonomous bootstrap: the agent should recover a missing shared
        # dependency cache instead of asking the user to run npm manually.
        npm = shutil.which("npm")
        if npm is None:
            raise RuntimeError("npm was not found on PATH; install Node.js/npm so AZIZ can bootstrap React dependencies automatically")
        lock = TEMPLATE_DIR / "package-lock.json"
        cmd = [npm, "ci"] if lock.exists() else [npm, "install"]
        result = subprocess.run(cmd, cwd=str(TEMPLATE_DIR), capture_output=True, text=True, timeout=240)
        if result.returncode != 0 or not (TEMPLATE_DIR / "node_modules").exists():
            detail = (result.stderr or result.stdout or "dependency installation failed")[-2500:]
            raise RuntimeError(f"Automatic React dependency bootstrap failed: {detail}")

    project_dir = Path(workspace_dir).resolve() / task_id.strip()
    (project_dir / "src" / "components" / "ui").mkdir(parents=True, exist_ok=True)
    (project_dir / "src" / "lib").mkdir(parents=True, exist_ok=True)

    for filename in ("package.json", "vite.config.js", "tsconfig.json",
                      "tailwind.config.js", "postcss.config.js", "index.html"):
        shutil.copy(TEMPLATE_DIR / filename, project_dir / filename)

    shutil.copy(TEMPLATE_DIR / "src" / "main.tsx", project_dir / "src" / "main.tsx")
    shutil.copy(TEMPLATE_DIR / "src" / "index.css", project_dir / "src" / "index.css")
    shutil.copy(TEMPLATE_DIR / "src" / "lib" / "utils.ts", project_dir / "src" / "lib" / "utils.ts")

    for ui_file in (TEMPLATE_DIR / "src" / "components" / "ui").glob("*"):
        if ui_file.is_file() and ui_file.suffix in {".tsx", ".jsx", ".js"}:
            shutil.copy(ui_file, project_dir / "src" / "components" / "ui" / ui_file.name)

    node_modules_target = project_dir / "node_modules"
    if node_modules_target.exists() or node_modules_target.is_symlink():
        if node_modules_target.is_symlink():
            node_modules_target.unlink()
        else:
            shutil.rmtree(node_modules_target)

    try:
        node_modules_target.symlink_to(TEMPLATE_DIR / "node_modules")
    except OSError:
        # Windows without Developer Mode/admin privileges (the common case)
        # can't create symlinks - fall back to a real copy. Slower, but
        # always works, and correctness matters more than speed here.
        shutil.copytree(TEMPLATE_DIR / "node_modules", node_modules_target)

    return project_dir


def _attach_process_output(process: subprocess.Popen) -> None:
    """Drain Vite output continuously so PIPE buffers cannot block the child."""
    process._aziz_stdout_lines = []
    process._aziz_stderr_lines = []
    def drain(stream, bucket):
        try:
            for line in iter(stream.readline, ""):
                if not line:
                    break
                bucket.append(line.rstrip())
                del bucket[:-200]
        except Exception:
            pass
    for stream, bucket in ((process.stdout, process._aziz_stdout_lines), (process.stderr, process._aziz_stderr_lines)):
        threading.Thread(target=drain, args=(stream, bucket), daemon=True).start()


def vite_process_output(process: subprocess.Popen, tail: int = 80) -> str:
    out = list(getattr(process, "_aziz_stdout_lines", []))[-tail:]
    err = list(getattr(process, "_aziz_stderr_lines", []))[-tail:]
    parts = []
    if out: parts.append("stdout:\n" + "\n".join(out))
    if err: parts.append("stderr:\n" + "\n".join(err))
    return "\n".join(parts)


def start_vite_dev_server(project_dir: Path, port: int) -> subprocess.Popen:
    """Start Vite on a strict port and continuously capture stdout/stderr."""
    npm_executable = shutil.which("npm")
    if npm_executable is None:
        raise RuntimeError("npm was not found on PATH. Make sure Node.js/npm is installed.")
    process = subprocess.Popen(
        [npm_executable, "run", "dev", "--", "--port", str(port), "--host", "0.0.0.0", "--strictPort"],
        cwd=str(project_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
    )
    _attach_process_output(process)
    return process


def start_vite_dev_server_with_recovery(project_dir: Path, preferred_port: int, progress=None, max_attempts: int = 4):
    """Recover only Vite startup/infrastructure failures; never spends an LLM repair attempt."""
    port = preferred_port
    last_output = ""
    for attempt in range(1, max_attempts + 1):
        if progress: progress("build", f"Starting Vite server (startup attempt {attempt}/{max_attempts}) on port {port}")
        process = start_vite_dev_server(project_dir, port)
        deadline = time.time() + 8.0
        while time.time() < deadline and process.poll() is None:
            output = vite_process_output(process, 30)
            if "local:" in output.lower() or "ready in" in output.lower() or "listening" in output.lower():
                return port, process, output
            time.sleep(0.15)
        if process.poll() is None:
            return port, process, vite_process_output(process)
        last_output = vite_process_output(process)
        low = last_output.lower()
        conflict = any(x in low for x in ("eaddrinuse", "address already in use", "port is already in use"))
        if progress:
            progress("build", f"Vite startup attempt {attempt} exited (code {process.returncode})." + (" Port conflict detected; selecting a new port." if conflict else " Capturing startup diagnostics."))
        if not conflict:
            return port, process, last_output
        port = _free_port()
    return port, process, last_output


def validate_via_dev_server(port: int, timeout: float = 15.0) -> list[str]:
    """
    The REAL validator for JSX: no Python `ast` equivalent exists, so we
    ask Vite's own esbuild transform to compile the component, by
    requesting it from the real running dev server. A real 500 response
    with a real compiler error means real broken JSX - we surface that
    error message directly instead of guessing.
    Returns a list of problems (empty = compiles cleanly).
    """
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            resp = urllib.request.urlopen(f"http://localhost:{port}/src/App.tsx", timeout=2)
            resp.read()
            return []  # 200 - real compile succeeded
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")
            return [f"Vite failed to compile App.tsx (HTTP {exc.code}): {_parse_vite_error_body(body)}"]
        except Exception as exc:
            last_error = exc
            time.sleep(0.4)
    return [f"Dev server never became reachable: {last_error}"]


def build_react_app(gateway, task_id: str, description: str, workspace_dir: str = "workspace"):
    """
    The full real chain: description -> model -> App.tsx -> scaffolded
    project -> real Vite dev server -> real compile validation.

    Returns (project_dir: Path, port: int, process: Popen, problems: list[str]).
    If problems is non-empty, the caller should terminate `process` - it's
    still returned so its stderr/logs can be inspected if needed.
    """
    jsx = generate_app_component(gateway, description)
    project_dir = scaffold_react_project(task_id, workspace_dir=workspace_dir)
    (project_dir / "src" / "App.tsx").write_text(jsx, encoding="utf-8")

    port = _free_port()
    process = start_vite_dev_server(project_dir, port)
    problems = validate_via_dev_server(port)

    return project_dir, port, process, problems
