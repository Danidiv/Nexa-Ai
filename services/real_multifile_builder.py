"""
Real Multi-File Builder — Stage 30-45% of the build path.

Takes ONE description and produces MULTIPLE real, correctly-linked files
(e.g. index.html + style.css + script.js), instead of one blob file.

Pattern:
    1. Ask the model for a PLAN: a short JSON list of files and what each does
    2. Generate each file's content one at a time, telling the model about
       the other files in the plan so references line up (e.g. HTML links
       to the exact CSS filename that will actually exist)
    3. Write every file to disk for real
    4. Do a basic sanity check: does each referenced file actually exist?

This is intentionally simple. No hidden magic, no stub records — every
function here either calls the model and returns real text, or writes a
real file and returns a real path.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from services.plan_compression import replan_oversized_plan
from dataclasses import dataclass


PLAN_SYSTEM_PROMPT = (
    "You are a software project planner. Given a short app description, "
    "output a JSON array (and NOTHING else - no markdown, no explanation) "
    "describing the files needed. Each item must have exactly these keys:\n"
    '  "path": relative file path, e.g. "index.html", "css/style.css", "js/script.js"\n'
    '  "purpose": one sentence describing what this file contains\n'
    "Keep it small: 2 to 10 files maximum; if more are proposed, the system will automatically compress the plan. Organize files into folders by "
    "type: put CSS files under a css/ folder, JS files under a js/ folder, "
    "and keep the HTML entry file (e.g. index.html) at the top level. "
    "Always use relative paths with no leading slash and no '..'. "
    "Output ONLY the JSON array."
)

FILE_SYSTEM_PROMPT = (
    "You are a code generator. Output ONLY raw file content - no markdown "
    "fences, no explanation, no commentary before or after the code."
)

FILE_USER_PROMPT_TEMPLATE = (
    "Build this: {description}\n\n"
    "This project has these files:\n{plan_json}\n\n"
    "Generate the COMPLETE content of ONE specific file: {target_path}\n"
    "What this file must contain: {target_purpose}\n\n"
    "Important: actually implement \"{description}\" - if this is the HTML "
    "file, it needs the real fields/elements that request implies (for a "
    "login page: actual username/password inputs and a submit button - "
    "not a generic welcome message or sample paragraph). "
    "If this file references another file from the list above (a "
    "stylesheet or script), use its exact path as shown."
)


@dataclass(frozen=True)
class PlannedFile:
    path: str
    purpose: str


def _strip_fences(text: str) -> str:
    text = text.strip()
    m = re.match(r"^```[a-zA-Z]*\n(.*)\n```$", text, re.DOTALL)
    return m.group(1).strip() if m else text


def _validate_relative_path(path: str) -> str:
    path = path.strip().lstrip("/")
    if not path or ".." in path.split("/"):
        raise ValueError(f"unsafe or empty file path in plan: {path!r}")
    return path


def generate_plan(gateway, description: str) -> list[PlannedFile]:
    """Ask the model for a small, real file plan. Returns validated PlannedFile list."""
    if not description or not description.strip():
        raise ValueError("description is required")

    messages = [
        {"role": "system", "content": PLAN_SYSTEM_PROMPT},
        {"role": "user", "content": description.strip()},
    ]
    raw = gateway.chat(messages, temperature=0.1, max_tokens=800)
    cleaned = _strip_fences(raw)

    try:
        items = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"model did not return valid JSON plan:\n{cleaned[:300]}") from exc

    if not isinstance(items, list) or not items:
        raise ValueError("plan must be a non-empty JSON array")
    if len(items) > 10:
        items = replan_oversized_plan(
            gateway, description, items, entry_path='index.html', extension=''
        )


    plan = []
    seen_paths = set()
    for item in items:
        if not isinstance(item, dict) or "path" not in item:
            raise ValueError(f"invalid plan item: {item!r}")
        path = _validate_relative_path(str(item["path"]))
        if path in seen_paths:
            raise ValueError(f"duplicate file path in plan: {path}")
        seen_paths.add(path)
        purpose = str(item.get("purpose", "")).strip()
        plan.append(PlannedFile(path=path, purpose=purpose))
    return plan


def generate_file_content(gateway, plan: list[PlannedFile], target: PlannedFile, description: str) -> str:
    """Generate the real content of ONE file. The actual task is put in the
    USER message (not buried in a long system prompt) because instruct-tuned
    models generally weight the user turn more heavily for what to actually
    do - this matters a lot for smaller/weaker local models that can ignore
    instructions stacked into a system message."""
    plan_json = json.dumps([{"path": p.path, "purpose": p.purpose} for p in plan], indent=2)
    user_prompt = FILE_USER_PROMPT_TEMPLATE.format(
        description=description.strip(),
        plan_json=plan_json,
        target_path=target.path,
        target_purpose=target.purpose,
    )
    messages = [
        {"role": "system", "content": FILE_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    raw = gateway.chat(messages, temperature=0.2, max_tokens=3000)
    return _strip_fences(raw)


_PLACEHOLDER_PHRASES = [
    "welcome to my web page",
    "this is a sample paragraph",
    "lorem ipsum",
    "this is a placeholder",
    "sample text goes here",
    "your content here",
    "hello world",
]


def find_generic_placeholder_content(html: str) -> list[str]:
    """
    Real, simple safety net: catch the specific failure mode we saw for
    real - a small model producing generic boilerplate ("Welcome to My Web
    Page", "This is a sample paragraph") instead of the actually requested
    UI. This is a heuristic phrase match, not a semantic check - it won't
    catch every case of "ignored the request", but it reliably catches the
    common generic-template phrases weak models fall back on.
    """
    lower = html.lower()
    return [phrase for phrase in _PLACEHOLDER_PHRASES if phrase in lower]


def ensure_box_sizing_reset(css: str) -> str:
    """
    Real, safe auto-repair: prepend a universal box-sizing reset if the CSS
    doesn't already have one.

    Why: the single most common bug small models produce is `width: 100%`
    plus `padding` on inputs/buttons with no box-sizing set, which makes
    the browser add padding ON TOP of the 100% width - so the element
    overflows past its container's right edge. This matches exactly the
    visual bug reported: inputs touching/overflowing the card border.

    `box-sizing: border-box` is a safe universal default - it essentially
    never breaks a correctly-designed layout, it only fixes this class of
    overflow bug. Idempotent: does nothing if a box-sizing rule already
    exists anywhere in the file.
    """
    if "box-sizing" in css.lower():
        return css  # already handled, don't duplicate
    reset = "*, *::before, *::after {\n  box-sizing: border-box;\n}\n\n"
    return reset + css


def apply_css_fixes(contents: dict[str, str]) -> dict[str, str]:
    """Apply real, safe CSS repairs to every .css file in a generated project."""
    fixed = {}
    for path, content in contents.items():
        if path.endswith(".css"):
            fixed[path] = ensure_box_sizing_reset(content)
        else:
            fixed[path] = content
    return fixed


def write_multifile_project(
    task_id: str, plan: list[PlannedFile], contents: dict[str, str], workspace_dir: str = "workspace"
) -> Path:
    """Write every planned file to disk for real. Returns the project directory."""
    if not task_id or not task_id.strip():
        raise ValueError("task_id is required")

    project_dir = Path(workspace_dir).resolve() / task_id.strip()
    project_dir.mkdir(parents=True, exist_ok=True)

    for planned in plan:
        content = contents.get(planned.path)
        if content is None:
            raise ValueError(f"missing generated content for {planned.path}")
        file_path = project_dir / planned.path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    return project_dir


def verify_references(project_dir: Path, plan: list[PlannedFile]) -> list[str]:
    """
    Basic real sanity check (not a stub): for every planned file, if any
    OTHER planned file's name is mentioned inside it (e.g. an <link href=...>
    or <script src=...>), confirm that referenced file actually got written.
    Returns a list of human-readable problems found (empty list = all good).
    """
    problems = []
    all_paths = {p.path for p in plan}
    for planned in plan:
        file_path = project_dir / planned.path
        if not file_path.exists():
            problems.append(f"{planned.path} was planned but never written")
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        for other in all_paths:
            if other == planned.path:
                continue
            if other in text and not (project_dir / other).exists():
                problems.append(f"{planned.path} references {other}, but {other} was not written")
    return problems


def build_multifile_project(gateway, task_id: str, description: str, workspace_dir: str = "workspace"):
    """
    The full real chain: description -> plan -> each file generated ->
    all written to disk -> reference check -> placeholder-content check.

    If a file comes back containing generic placeholder boilerplate
    (a real failure mode of weaker models), we retry that ONE file once
    with a more forceful prompt before giving up and reporting it.

    Returns (project_dir: Path, plan: list[PlannedFile], problems: list[str])
    problems includes both broken cross-references AND any placeholder
    content that survived a retry.
    """
    plan = generate_plan(gateway, description)
    contents = {}
    placeholder_warnings = []

    for planned in plan:
        content = generate_file_content(gateway, plan, planned, description)
        placeholders = find_generic_placeholder_content(content)

        if placeholders and planned.path.endswith((".html", ".htm")):
            # One retry with a more forceful, shorter, harder-to-ignore nudge.
            retry_messages = [
                {"role": "system", "content": FILE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Write the HTML for: {description}. "
                        f"Do NOT write a generic welcome page. "
                        f"Include the actual real form fields/elements this needs. "
                        f"Output only the HTML."
                    ),
                },
            ]
            retry_raw = gateway.chat(retry_messages, temperature=0.2, max_tokens=3000)
            retried_content = _strip_fences(retry_raw)
            if not find_generic_placeholder_content(retried_content):
                content = retried_content
            else:
                placeholder_warnings.append(
                    f"{planned.path}: model produced generic placeholder content "
                    f"even after retry ({placeholders})"
                )

        contents[planned.path] = content

    contents = apply_css_fixes(contents)
    project_dir = write_multifile_project(task_id, plan, contents, workspace_dir=workspace_dir)
    problems = verify_references(project_dir, plan) + placeholder_warnings
    return project_dir, plan, problems
