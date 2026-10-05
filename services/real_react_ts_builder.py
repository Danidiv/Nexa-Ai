"""
Real React + TypeScript + shadcn/ui Builder — the Lovable-parity track.

Same pattern as real_react_multifile_builder.py, upgraded to:
    - generate .tsx instead of .jsx, with real prop interfaces
    - the model can use REAL shadcn/ui primitives already in the template
      (Button, Card, Input) instead of hand-rolling everything from divs
    - TWO real validators instead of one: the existing per-file Vite
      compile check (catches syntax errors), PLUS a real `tsc --noEmit`
      run across the whole project (catches real TYPE errors that Vite's
      esbuild transform does not check, since esbuild strips types
      without verifying them)
"""
from __future__ import annotations

import json
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from services.plan_compression import replan_oversized_plan

from services.real_react_builder import _free_port, start_vite_dev_server
from services.real_react_multifile_builder import (
    _strip_fences,
    _component_name_from_path,
    extract_destructured_props,
    extract_props_passed,
)

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "react_ts_scaffold_test"

AVAILABLE_PRIMITIVES = (
    "Button (@/components/ui/button) - props: variant ('default'|'destructive'|"
    "'outline'|'secondary'|'ghost'|'link'), size ('default'|'sm'|'lg'|'icon'), "
    "plus all normal <button> props\n"
    "Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter "
    "(@/components/ui/card) - compose them like real shadcn/ui cards\n"
    "Input (@/components/ui/input) - a styled <input>, all normal <input> props\n"
    "cn (@/lib/utils) - merges class names safely, use for conditional classes"
)

PLAN_SYSTEM_PROMPT = (
    "You are a React + TypeScript project planner. Given an app description, "
    "output a JSON array (and NOTHING else) of the component files needed. "
    "Each item must have exactly these keys:\n"
    '  "path": relative path under src/, e.g. "App.tsx" or '
    '"components/PricingCard.tsx"\n'
    '  "purpose": one sentence describing what this component does\n'
    "Rules:\n"
    "- Exactly ONE item must have path exactly \"App.tsx\".\n"
    "- Every other item's path must start with \"components/\" and end in "
    "\".tsx\", with a PascalCase filename.\n"
    "- Keep it small: 2 to 10 files total, including App.tsx.\n"
    "- Output ONLY the JSON array."
)

COMPONENT_SYSTEM_PROMPT = (
    "You are a React + TypeScript component generator. Output ONLY raw "
    ".tsx file content - no markdown fences, no explanation."
)

COMPONENT_USER_PROMPT_TEMPLATE = (
    "Build this: {description}\n\n"
    "This project has these component files:\n{plan_json}\n\n"
    "Generate the COMPLETE content of ONE file: src/{target_path}\n"
    "What this component must do: {target_purpose}\n\n"
    "These real, already-available shadcn/ui primitives may be imported "
    "and used - PREFER them over hand-rolled divs/buttons:\n{primitives}\n\n"
    "Requirements:\n"
    "- Export a single default function component named {component_name}.\n"
    "- Write real TypeScript: define a props interface/type for anything "
    "this component receives, e.g. `interface {component_name}Props {{ "
    "name: string; price: string }}` and type the function accordingly.\n"
    "- Use Tailwind CSS utility classes for styling.\n"
    "- If this component needs another component from the plan above, "
    "import it with its EXACT relative path, using a default import.\n"
    "- If this component renders MULTIPLE instances of the same child "
    "side by side, arrange them with a Tailwind grid/flex layout - never "
    "let repeated items just stack full-width.\n"
    "- If a prop represents a price/currency, include the symbol in "
    "EXACTLY ONE place - either in the prop value or the template, never "
    "both.\n"
    "- Do NOT import any package other than 'react' and the shadcn/ui "
    "primitives listed above.\n"
    "- Output ONLY the raw .tsx file content."
)


@dataclass(frozen=True)
class PlannedComponent:
    path: str
    purpose: str
    component_name: str


def generate_plan(gateway, description: str) -> list[PlannedComponent]:
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
            gateway, description, items, entry_path='App.tsx', extension='.tsx'
        )


    plan = []
    seen_paths = set()
    app_count = 0
    for item in items:
        if not isinstance(item, dict) or "path" not in item:
            raise ValueError(f"invalid plan item: {item!r}")
        path = str(item["path"]).strip().lstrip("/")
        if ".." in path.split("/"):
            raise ValueError(f"unsafe path in plan: {path!r}")
        if path in seen_paths:
            raise ValueError(f"duplicate path in plan: {path}")
        seen_paths.add(path)

        if path == "App.tsx":
            app_count += 1
        elif not (path.startswith("components/") and path.endswith(".tsx")):
            raise ValueError(f"invalid component path (must be App.tsx or components/*.tsx): {path!r}")

        component_name = _component_name_from_path(path)
        purpose = str(item.get("purpose", "")).strip()
        plan.append(PlannedComponent(path=path, purpose=purpose, component_name=component_name))

    if app_count != 1:
        raise ValueError(f"plan must contain exactly one App.tsx, found {app_count}")

    return plan


def generate_component(gateway, plan: list[PlannedComponent], target: PlannedComponent, description: str) -> str:
    plan_json = json.dumps(
        [{"path": p.path, "purpose": p.purpose, "exports": p.component_name} for p in plan], indent=2
    )
    user_prompt = COMPONENT_USER_PROMPT_TEMPLATE.format(
        description=description.strip(),
        plan_json=plan_json,
        target_path=target.path,
        target_purpose=target.purpose,
        component_name=target.component_name,
        primitives=AVAILABLE_PRIMITIVES,
    )
    messages = [
        {"role": "system", "content": COMPONENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    raw = gateway.chat(messages, temperature=0.2, max_tokens=3500)
    tsx = _strip_fences(raw)

    if "export default" not in tsx:
        raise ValueError(f"{target.path}: model did not return a default-exported component")
    return tsx


def find_prop_contract_mismatches_detailed(plan: list[PlannedComponent], contents: dict[str, str]) -> list[dict]:
    results = []
    for planned in plan:
        if planned.path == "App.tsx":
            continue
        destructured = extract_destructured_props(contents[planned.path], planned.component_name)
        if not destructured:
            continue
        passed_anywhere = set()
        used_at_least_once = False
        for other_path, other_content in contents.items():
            if other_path == planned.path:
                continue
            props_here = extract_props_passed(other_content, planned.component_name)
            if f"<{planned.component_name}" in other_content:
                used_at_least_once = True
            passed_anywhere |= props_here
        if not used_at_least_once:
            continue
        missing = destructured - passed_anywhere
        if missing:
            results.append({
                "path": planned.path,
                "component_name": planned.component_name,
                "missing": sorted(missing),
                "actually_passed": sorted(passed_anywhere),
            })
    return results


def _retry_component_with_correction(gateway, plan, target, description, mismatch) -> str:
    plan_json = json.dumps(
        [{"path": p.path, "purpose": p.purpose, "exports": p.component_name} for p in plan], indent=2
    )
    correction = (
        f"IMPORTANT CORRECTION: your previous version destructured prop(s) "
        f"{mismatch['missing']}, but the actual caller(s) pass exactly these "
        f"prop names: {mismatch['actually_passed']}. Rewrite using EXACTLY "
        f"those prop names, with a correct TypeScript props interface."
    )
    user_prompt = COMPONENT_USER_PROMPT_TEMPLATE.format(
        description=description.strip(),
        plan_json=plan_json,
        target_path=target.path,
        target_purpose=target.purpose,
        component_name=target.component_name,
        primitives=AVAILABLE_PRIMITIVES,
    ) + "\n\n" + correction

    messages = [
        {"role": "system", "content": COMPONENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    raw = gateway.chat(messages, temperature=0.2, max_tokens=3500)
    tsx = _strip_fences(raw)
    if "export default" not in tsx:
        raise ValueError(f"{target.path}: retry did not return a default-exported component")
    return tsx


def scaffold_react_ts_project(task_id: str, workspace_dir: str = "workspace") -> Path:
    """Real scaffold copy, including the shadcn/ui primitives and real Tailwind config."""
    if not TEMPLATE_DIR.exists():
        raise RuntimeError(f"TS+shadcn template not found at {TEMPLATE_DIR}")
    if not (TEMPLATE_DIR / "node_modules").exists():
        raise RuntimeError(f"Template has no node_modules - run 'npm install' in {TEMPLATE_DIR} first")

    project_dir = Path(workspace_dir).resolve() / task_id.strip()
    (project_dir / "src" / "components" / "ui").mkdir(parents=True, exist_ok=True)
    (project_dir / "src" / "lib").mkdir(parents=True, exist_ok=True)

    for filename in (
        "package.json", "vite.config.ts", "tsconfig.json", "tsconfig.node.json",
        "postcss.config.js", "tailwind.config.js", "index.html",
    ):
        shutil.copy(TEMPLATE_DIR / filename, project_dir / filename)
    shutil.copy(TEMPLATE_DIR / "src" / "main.tsx", project_dir / "src" / "main.tsx")
    shutil.copy(TEMPLATE_DIR / "src" / "index.css", project_dir / "src" / "index.css")
    shutil.copy(TEMPLATE_DIR / "src" / "lib" / "utils.ts", project_dir / "src" / "lib" / "utils.ts")
    for ui_file in (TEMPLATE_DIR / "src" / "components" / "ui").glob("*.tsx"):
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
        shutil.copytree(TEMPLATE_DIR / "node_modules", node_modules_target)

    return project_dir


def write_components(project_dir: Path, plan: list[PlannedComponent], contents: dict[str, str]) -> None:
    src_dir = project_dir / "src"
    for planned in plan:
        content = contents.get(planned.path)
        if content is None:
            raise ValueError(f"missing generated content for {planned.path}")
        file_path = src_dir / planned.path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")


def validate_all_components(port: int, plan: list[PlannedComponent], timeout: float = 15.0) -> list[str]:
    problems = []
    deadline = time.time() + timeout
    server_ready = False
    first_path = plan[0].path
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://localhost:{port}/src/{first_path}", timeout=2)
            server_ready = True
            break
        except urllib.error.HTTPError:
            server_ready = True
            break
        except Exception:
            time.sleep(0.4)
    if not server_ready:
        return [f"Dev server on port {port} never became reachable within {timeout}s"]

    for planned in plan:
        try:
            urllib.request.urlopen(f"http://localhost:{port}/src/{planned.path}", timeout=5)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")
            problems.append(f"{planned.path}: Vite failed to compile (HTTP {exc.code}):\n{body[:400]}")
        except Exception as exc:
            problems.append(f"{planned.path}: request failed: {exc}")
    return problems


def run_type_check(project_dir: Path, timeout: float = 60.0) -> list[str]:
    """
    Real second validator: actually run `tsc --noEmit` across the whole
    project. This catches real TYPE errors (wrong prop types, missing
    required props by TYPE, etc.) that Vite's esbuild transform does NOT
    check - esbuild strips TypeScript types for speed without verifying
    them at all. Only the real TypeScript compiler can.
    """
    try:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit"],
            cwd=str(project_dir),
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return [f"Type-check timed out after {timeout}s"]
    except FileNotFoundError:
        return ["npx not found - is Node.js/npm installed?"]

    if result.returncode != 0:
        output = (result.stdout or "") + (result.stderr or "")
        return [f"TypeScript found real type errors:\n{output[:1500]}"]
    return []


def build_multi_component_react_ts_app(gateway, task_id: str, description: str, workspace_dir: str = "workspace"):
    """
    The full real chain: description -> plan -> each .tsx component
    generated (with real shadcn/ui primitives available) -> real
    prop-contract check + corrective retry -> real Vite compile check per
    file -> real `tsc --noEmit` type-check across the whole project.

    Returns (project_dir, port, process, plan, problems).
    """
    plan = generate_plan(gateway, description)
    contents = {}
    for planned in plan:
        contents[planned.path] = generate_component(gateway, plan, planned, description)

    mismatches = find_prop_contract_mismatches_detailed(plan, contents)
    plan_by_path = {p.path: p for p in plan}
    unresolved = []
    for mismatch in mismatches:
        target = plan_by_path[mismatch["path"]]
        try:
            retried = _retry_component_with_correction(gateway, plan, target, description, mismatch)
        except ValueError as exc:
            unresolved.append(str(exc))
            continue
        contents[mismatch["path"]] = retried
        recheck = find_prop_contract_mismatches_detailed(plan, contents)
        still_broken = next((m for m in recheck if m["path"] == mismatch["path"]), None)
        if still_broken:
            unresolved.append(
                f"{mismatch['path']}: still expects prop(s) {still_broken['missing']} after retry"
            )

    project_dir = scaffold_react_ts_project(task_id, workspace_dir=workspace_dir)
    write_components(project_dir, plan, contents)

    port = _free_port()
    process = start_vite_dev_server(project_dir, port)
    problems = unresolved + validate_all_components(port, plan)

    # Only bother with the (slower) real type-check if the faster checks
    # already passed - no point type-checking code we know is already broken.
    if not problems:
        problems += run_type_check(project_dir)

    return project_dir, port, process, plan, problems
