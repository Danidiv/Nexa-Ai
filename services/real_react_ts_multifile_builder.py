"""
Real TypeScript + shadcn/ui Multi-Component Builder — the Lovable-parity
track: real TypeScript (with an actual tsc type-check as an additional
validator, not just esbuild's syntax-only strip), real shadcn/ui component
primitives (Button, Card, Input) the model can genuinely import and use.

Reuses the generic (extension-agnostic) pieces from
real_react_multifile_builder.py - the plan/component dataclass, the prop-
extraction regexes, and the per-file Vite-compile validator all work
identically on .tsx as on .jsx. Only the prompts, the scaffold (different
template with more files), and the NEW real tsc type-check are specific
to this track.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from services.plan_compression import replan_oversized_plan

from services.real_react_builder import _strip_fences, _free_port, start_vite_dev_server, ensure_npm_dependency, missing_dependency_from_vite_error
from services.real_react_multifile_builder import (
    PlannedComponent,
    _component_name_from_path,
    write_components,
    validate_all_components,
    find_prop_contract_mismatches_detailed,
    _retry_caller_with_missing_props,
    validate_and_repair_imports,
    _runtime_target_path,
    _install_runtime_reporter,
    _generate_missing_local_resource,
)

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "react_ts_scaffold_test"

TEMPLATE_FILES = [
    "package.json", "vite.config.ts", "tsconfig.json", "tsconfig.node.json",
    "postcss.config.js", "tailwind.config.js", "index.html",
]
TEMPLATE_SRC_FILES = ["main.tsx", "index.css"]
TEMPLATE_UI_COMPONENTS = ["button.tsx", "card.tsx", "input.tsx", "badge.tsx"]

PLAN_SYSTEM_PROMPT = (
    "You are a React+TypeScript project planner. Given an app description, "
    "output a JSON array (and NOTHING else - no markdown, no explanation) "
    "of the component files needed. Each item must have exactly these keys:\n"
    '  "path": relative path under src/, e.g. "App.tsx" or '
    '"components/PricingCard.tsx"\n'
    '  "purpose": one sentence describing what this component does\n'
    "Rules:\n"
    "- Exactly ONE item must have path exactly \"App.tsx\" - this is the "
    "entry component that main.tsx renders.\n"
    "- Every other item's path must start with \"components/\" and end "
    "in \".tsx\", with a PascalCase filename.\n"
    "- Keep it small: 2 to 10 files total, including App.tsx.\n"
    "- Output ONLY the JSON array."
)

COMPONENT_SYSTEM_PROMPT = (
    "You are a React+TypeScript component generator. Output ONLY raw "
    ".tsx file content - no markdown fences, no explanation."
)

COMPONENT_USER_PROMPT_TEMPLATE = (
    "Build this: {description}\n\n"
    "This project has these component files:\n{plan_json}\n\n"
    "Generate the COMPLETE content of ONE file: src/{target_path}\n"
    "What this component must do: {target_purpose}\n\n"
    "Requirements:\n"
    "- Use TypeScript. Define a `Props` interface (or inline type) for "
    "this component's props if it takes any, and type them correctly "
    "(e.g. `title: string`, `price: string`, `onClick: () => void`).\n"
    "- Export a single default function component named {component_name}.\n"
    "- Real shadcn/ui components are ALREADY AVAILABLE - use them instead "
    "of plain HTML where appropriate:\n"
    "    import {{ Button }} from '@/components/ui/button'\n"
    "    import {{ Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter }} from '@/components/ui/card'\n"
    "    import {{ Input }} from '@/components/ui/input'\n"
    "- Also use Tailwind utility classes for any additional layout/spacing.\n"
    "- If this component needs another component from the list above, "
    "import it with its EXACT relative path from this file's location, "
    "using a default import.\n"
    "- If this component renders MULTIPLE instances of the same child "
    "component side by side, arrange them with a Tailwind grid or flex "
    "layout - e.g. <div className=\"grid grid-cols-1 md:grid-cols-3 gap-6\">.\n"
    "- If a prop represents a price or currency amount, include the "
    "currency symbol in EXACTLY ONE place, never both.\n"
    "- The pre-installed shadcn/ui components include Button, Card, Input, Label, and Badge at '@/components/ui/...'. "
    "- Do NOT import any package other than 'react' and the shadcn "
    "'@/components/ui/*' paths shown above.\n"
    "- Output ONLY the raw .tsx file content."
)


def generate_plan(gateway, description: str) -> list[PlannedComponent]:
    """Real plan call, TSX-specific validation (App.tsx required, .tsx extensions)."""
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


def _has_default_export(tsx: str) -> bool:
    """
    Recognize the common valid ways a component can be the default export,
    not just the literal substring "export default". A small local model
    that writes `export { PricingCard as default }` (valid TS, no
    "export default" substring) was previously rejected as if it had
    produced no default export at all.
    """
    return bool(re.search(r"export\s+default\b", tsx)) or bool(
        re.search(r"export\s*\{[^}]*\bas\s+default\b[^}]*\}", tsx)
    )


def generate_component(
    gateway, plan: list[PlannedComponent], target: PlannedComponent, description: str, max_attempts: int = 2
) -> str:
    plan_json = json.dumps(
        [{"path": p.path, "purpose": p.purpose, "exports": p.component_name} for p in plan], indent=2
    )
    user_prompt = COMPONENT_USER_PROMPT_TEMPLATE.format(
        description=description.strip(),
        plan_json=plan_json,
        target_path=target.path,
        target_purpose=target.purpose,
        component_name=target.component_name,
    )
    messages = [
        {"role": "system", "content": COMPONENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    last_tsx = ""
    for attempt in range(max_attempts):
        raw = gateway.chat(messages, temperature=0.2, max_tokens=3000)
        tsx = _strip_fences(raw)
        if _has_default_export(tsx):
            return tsx
        last_tsx = tsx
        # Retry once with a sharper, more explicit correction before giving
        # up - the same forgiving pattern already used for prop-contract
        # mismatches below, just applied to this failure mode too.
        messages = messages[:2] + [
            {"role": "assistant", "content": raw},
            {
                "role": "user",
                "content": (
                    "That response is missing a default export. Output ONLY "
                    f"the raw .tsx file content for src/{target.path}, and it "
                    f"MUST end with a line reading exactly:\n"
                    f"export default {target.component_name};\n"
                    "No markdown fences, no explanation, no other text."
                ),
            },
        ]

    raise ValueError(
        f"{target.path}: model did not return a default-exported component after "
        f"{max_attempts} attempts. Got:\n{last_tsx[:400]}"
    )


def _retry_component_with_correction(
    gateway, plan: list[PlannedComponent], target: PlannedComponent, description: str, mismatch: dict
) -> str:
    plan_json = json.dumps(
        [{"path": p.path, "purpose": p.purpose, "exports": p.component_name} for p in plan], indent=2
    )
    correction = (
        f"IMPORTANT CORRECTION: your previous version of this component "
        f"destructured prop(s) {mismatch['missing']}, but the actual caller(s) in "
        f"this project pass exactly these prop names: {mismatch['actually_passed']}. "
        f"Rewrite the component to destructure and use EXACTLY the prop names "
        f"the caller actually passes - do not invent different names."
    )
    user_prompt = COMPONENT_USER_PROMPT_TEMPLATE.format(
        description=description.strip(),
        plan_json=plan_json,
        target_path=target.path,
        target_purpose=target.purpose,
        component_name=target.component_name,
    ) + "\n\n" + correction

    messages = [
        {"role": "system", "content": COMPONENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    raw = gateway.chat(messages, temperature=0.2, max_tokens=3000)
    tsx = _strip_fences(raw)
    if not _has_default_export(tsx):
        raise ValueError(f"{target.path}: retry did not return a default-exported component. Got:\n{tsx[:400]}")
    return tsx


def _retry_component_with_type_error(
    gateway, plan: list[PlannedComponent], target: PlannedComponent, description: str, tsc_output: str
) -> str:
    """
    Feed a real `tsc --noEmit` error back to the model for the one file it
    points at, and ask for a corrected version - the same self-correction
    pattern used above for prop-name mismatches and missing default
    exports, applied to genuine TypeScript type errors instead of just
    surfacing them as an unrecoverable build failure.
    """
    plan_json = json.dumps(
        [{"path": p.path, "purpose": p.purpose, "exports": p.component_name} for p in plan], indent=2
    )
    correction = (
        "IMPORTANT CORRECTION: running `tsc --noEmit` on your previous version "
        f"of this file produced this real TypeScript error:\n{tsc_output.strip()[:800]}\n\n"
        "Rewrite the file so this specific error is fixed - e.g. if a value can "
        "be `undefined` (from array .find(), an optional prop, etc.) either "
        "give it a fallback default, narrow it with a check first, or mark the "
        "receiving prop/type as optional (`prop?: string`) - do not just "
        "silence the error with `as string` or `any`."
    )
    user_prompt = COMPONENT_USER_PROMPT_TEMPLATE.format(
        description=description.strip(),
        plan_json=plan_json,
        target_path=target.path,
        target_purpose=target.purpose,
        component_name=target.component_name,
    ) + "\n\n" + correction

    messages = [
        {"role": "system", "content": COMPONENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    raw = gateway.chat(messages, temperature=0.2, max_tokens=3000)
    tsx = _strip_fences(raw)
    if not _has_default_export(tsx):
        raise ValueError(f"{target.path}: type-error retry did not return a default-exported component. Got:\n{tsx[:400]}")
    return tsx


def _retry_component_with_vite_error(
    gateway, plan: list[PlannedComponent], target: PlannedComponent, description: str, vite_message: str
) -> str:
    """
    Corrective retry for a REAL Vite/esbuild compile failure (unclosed
    JSX tag, unbalanced braces, truncated output, etc.) - the one class
    of bug _has_default_export can't catch, since a file can contain
    "export default" and still be otherwise malformed. vite_message is
    the parsed one-line summary from _parse_vite_error_body, not the raw
    HTML error page tsc never sees this - it's a Vite/esbuild-level
    parse failure, so it can slip through even after a clean tsc pass.
    """
    plan_json = json.dumps(
        [{"path": p.path, "purpose": p.purpose, "exports": p.component_name} for p in plan], indent=2
    )
    correction = (
        f"IMPORTANT CORRECTION: your previous version of this file FAILED TO COMPILE "
        f"in a real Vite dev server with this real error:\n{vite_message[:600]}\n\n"
        f"Produce a COMPLETE, syntactically valid file this time - every opening JSX "
        f"tag must have a matching closing tag (or be self-closing), every brace and "
        f"parenthesis must be balanced, and the file must not be cut off early."
    )
    user_prompt = COMPONENT_USER_PROMPT_TEMPLATE.format(
        description=description.strip(),
        plan_json=plan_json,
        target_path=target.path,
        target_purpose=target.purpose,
        component_name=target.component_name,
    ) + "\n\n" + correction

    messages = [
        {"role": "system", "content": COMPONENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    raw = gateway.chat(messages, temperature=0.2, max_tokens=3000)
    tsx = _strip_fences(raw)
    if not _has_default_export(tsx):
        raise ValueError(f"{target.path}: vite-error retry did not return a default-exported component. Got:\n{tsx[:400]}")
    return tsx


_TSC_FILE_RE = re.compile(r"src[/\\]([\w./\\-]+\.tsx)")
# Pure parser/syntax-level failures (1xxx codes) rather than type errors -
# most commonly caused by an unescaped apostrophe/quote inside a string
# literal, which then cascades into a wall of unrelated-looking
# downstream errors (wrong token expected, unexpected identifier, etc.)
# that are just parser confusion from the ONE real problem, not separate
# bugs to fix individually.
_SYNTAX_ERROR_RE = re.compile(
    r"src[/\\]([\w./\\-]+\.tsx)\((\d+),(\d+)\): error (TS1\d{3}): ([^\n]*?)(?=\s+src[/\\]|\s*$)"
)


def _syntax_error_targets(tsc_output: str, plan: list[PlannedComponent]):
    """Keep only the EARLIEST syntax error per file - everything after it
    on the same file is almost always cascading parser confusion, not an
    independent bug, so surfacing all of them would just add noise."""
    plan_by_path = {p.path: p for p in plan}
    earliest: dict[str, tuple[int, str, str, str]] = {}
    for file_path, line, col, code, msg in _SYNTAX_ERROR_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        if plan_by_path.get(file_path) is None:
            continue
        line_num = int(line)
        if file_path not in earliest or line_num < earliest[file_path][0]:
            earliest[file_path] = (line_num, col, code, msg.strip())
    fixes: dict[str, list[str]] = {}
    for file_path, (line_num, col, code, msg) in earliest.items():
        fixes.setdefault(file_path, []).append(
            f"This file has a real SYNTAX error (not a type error), at line {line_num}, "
            f"column {col}: {code} \"{msg}\". Any other errors reported after this point "
            f"in the same file are almost certainly cascading parser confusion caused by "
            f"this ONE root problem, not separate bugs - ignore them and focus only on "
            f"this. The most common real cause of this is an apostrophe or quote "
            f"character INSIDE a string that wasn't escaped (e.g. writing 'We're proud' "
            f"with a plain apostrophe inside single quotes closes the string early, "
            f"corrupting everything that follows). Rewrite the ENTIRE file from "
            f"scratch, and for any text containing an apostrophe or quote, either use "
            f"double quotes for that string, escape it with a backslash, or use a "
            f"template literal with backticks instead."
        )
    return fixes


_MISSING_PROP_RE = re.compile(
    r"Property '(\w+)' does not exist on type '(?:IntrinsicAttributes\s*&\s*)?(\w+)'"
)
_MISSING_IMPORT_RE = re.compile(
    r"src[/\\]([\w./\\-]+\.tsx)\(\d+,\d+\): error TS2304: Cannot find name '(\w+)'"
)
_MISSING_REQUIRED_PROP_RE = re.compile(
    r"src[/\\]([\w./\\-]+\.tsx)\(\d+,\d+\): error TS2741: Property '(\w+)' is missing in "
    r"type '[^']*' but required in type '(?:IntrinsicAttributes\s*&\s*)?(\w+)'"
)
# TS2739's shape for a component whose props are typed via a plain
# `(props: XProps)` parameter (no destructuring) rather than TS2741's
# one-property-at-a-time shape - lists every missing prop at once, e.g.
# "Type '{}' is missing the following properties from type 'HeroSectionProps':
# title, ctaText, onCtaClick". This is the ONLY way this class of mistake
# ever surfaces: extract_destructured_props can't see props accessed as
# `props.x` instead of destructured, so the JS-level heuristic check
# never even runs for a component written this way - it would otherwise
# reach the end user as an unrecovered tsc failure.
_MISSING_REQUIRED_PROPS_MULTI_RE = re.compile(
    r"src[/\\]([\w./\\-]+\.tsx)\(\d+,\d+\): error TS2739: Type '\{\}' is missing the "
    r"following properties from type '(?:IntrinsicAttributes\s*&\s*)?(\w+)': ([\w, ]+)"
)


def _missing_required_props_multi_targets(tsc_output: str, plan: list[PlannedComponent]):
    """Collect TS2739 matches into the same {file_path: [notes]} shape as
    the other detectors, so a caller missing several different components'
    props all at once (a common real pattern: several bare `<X />` calls
    in the same App.tsx) gets ONE combined retry instead of one overwriting
    retry per component - which matters doubly on a local model: each
    retry is a full inference call, and retrying the SAME file repeatedly
    from scratch (rather than batched) can silently undo an earlier fix
    to that same file."""
    plan_by_path = {p.path: p for p in plan}
    fixes: dict[str, list[str]] = {}
    for file_path, interface_name, props_csv in _MISSING_REQUIRED_PROPS_MULTI_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        if plan_by_path.get(file_path) is None:
            continue
        owner_name = interface_name[: -len("Props")] if interface_name.endswith("Props") else interface_name
        props_list = [p.strip() for p in props_csv.split(",") if p.strip()]
        fixes.setdefault(file_path, []).append(
            f"You render `<{owner_name}>` without passing ANY of its required props "
            f"(tsc: \"Type '{{}}' is missing the following properties from type "
            f"'{interface_name}': {', '.join(props_list)}\"). Add all of "
            f"{props_list} with real, appropriate data - do not remove the prop "
            f"requirement from the child instead, since that would just hide "
            f"missing content."
        )
    return fixes


_REACT_UMD_GLOBAL_RE = re.compile(
    r"src[/\\]([\w./\\-]+\.tsx)\(\d+,\d+\): error TS2686: 'React' refers to a UMD global"
)
_IMPLICIT_ANY_PARAM_RE = re.compile(
    r"src[/\\]([\w./\\-]+\.tsx)\(\d+,\d+\): error TS7006: Parameter '(\w+)' implicitly has an 'any' type"
)
# TS2614: the file did `import { X } from '...'` (a named import) for a
# component that's actually a DEFAULT export - tsc's own suggested fix is
# right there in the message ("Did you mean to use 'import X from ...'
# instead?"), so this is purely mechanical to detect and correct.
_NAMED_IMPORT_SHOULD_BE_DEFAULT_RE = re.compile(
    r"src[/\\]([\w./\\-]+\.tsx)\(\d+,\d+\): error TS2614: Module '([^']*)' has no exported "
    r"member '(\w+)'"
)


def _named_import_should_be_default_targets(tsc_output: str, plan: list[PlannedComponent]):
    """Collect TS2614 matches - a named import used for one of our own
    planned components, which are always written as a default export."""
    plan_by_path = {p.path: p for p in plan}
    plan_by_component = {p.component_name: p for p in plan}
    fixes: dict[str, list[str]] = {}
    for file_path, module_path, member_name in _NAMED_IMPORT_SHOULD_BE_DEFAULT_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        module_path = module_path.strip('"')
        if plan_by_path.get(file_path) is None:
            continue
        if plan_by_component.get(member_name) is None:
            continue  # not one of our own components - leave to generic fallback
        fixes.setdefault(file_path, []).append(
            f"You wrote `import {{ {member_name} }} from '{module_path}'` (a named "
            f"import), but tsc says that module has no exported member named "
            f"'{member_name}' - {member_name} is a DEFAULT export. Change this line "
            f"to `import {member_name} from '{module_path}';` (no curly braces)."
        )
    return fixes


# Catch-all for "Property 'X' is missing in type 'A' but required in type 'B'"
# regardless of the surrounding error code (TS2322, TS2719, TS2741) or
# whether B is a plain interface name or an inline object-literal type -
# the two more specific detectors above only match a subset of the shapes
# this same underlying "your local data/type doesn't match what's
# actually required" problem can take.
_MISSING_PROPERTY_ANY_RE = re.compile(
    r"src[/\\]([\w./\\-]+\.tsx)\(\d+,\d+\): error TS\d+:.*?"
    r"Property '(\w+)' is missing in type '[^']*' but required in type '([^']*)'",
    re.DOTALL,
)
_OBJECT_LITERAL_EXCESS_PROP_RE = re.compile(
    r"src[/\\]([\w./\\-]+\.tsx)\(\d+,\d+\): error TS2353: Object literal may only specify "
    r"known properties, and '(\w+)' does not exist in type '(\w+)'"
)
_FUNCTION_SIGNATURE_MISMATCH_RE = re.compile(
    r"src[/\\]([\w./\\-]+\.tsx)\(\d+,\d+\): error TS2322: Type '([^']+)' is not assignable to "
    r"type '([^']+)'\.\s*Types of parameters '(\w+)' and '(\w+)' are incompatible"
)


def _split_interface_members(body: str) -> list[str]:
    """Split an interface/type-literal body on `;` (or bare newlines, which
    TS also accepts between members) at bracket-depth 0, so a nested
    object-typed field doesn't get split apart."""
    parts, current, depth = [], [], 0
    normalized = body.replace("\n", ";")
    for ch in normalized:
        if ch in "{[(":
            depth += 1
        elif ch in "}])":
            depth -= 1
        if ch == ";" and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current))
    return parts


def _interface_field_names(contents: dict[str, str], type_name: str) -> list[str] | None:
    """Find `interface TypeName { ... }` or `type TypeName = { ... }` in
    ANY file's content and return its real field names, so a corrective
    note can tell the model exactly what to rename a wrong field to,
    instead of vaguely pointing at "the other file"."""
    pattern = re.compile(
        rf"(?:interface\s+{re.escape(type_name)}\s*\{{|type\s+{re.escape(type_name)}\s*=\s*\{{)"
        rf"((?:[^{{}}]|\{{[^{{}}]*\}})*)\}}"
    )
    for content in contents.values():
        m = pattern.search(content)
        if m:
            fields = []
            for segment in _split_interface_members(m.group(1)):
                segment = segment.strip()
                if not segment:
                    continue
                name = segment.split(":", 1)[0].split("?", 1)[0].strip()
                if re.match(r"^\w+$", name):
                    fields.append(name)
            return fields
    return None


def _object_literal_excess_prop_targets(tsc_output: str, plan: list[PlannedComponent], contents: dict[str, str]):
    """
    TS2353: a data object literal (often an array of items passed as a
    prop) uses a field name a real type doesn't have - typically because
    the caller and the type's owner drifted onto different names for the
    same concept (e.g. `name` vs `title`). Unlike a missing/extra JSX
    prop, this is DATA reshaping, and the tsc message alone doesn't say
    what the field should have been called - so this looks up the type's
    real declaration (wherever it lives) and tells the model the exact
    field names to use instead of guessing.
    """
    plan_by_path = {p.path: p for p in plan}
    fixes: dict[str, list[str]] = {}
    seen: set[tuple[str, str]] = set()
    for file_path, bad_field, type_name in _OBJECT_LITERAL_EXCESS_PROP_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        if plan_by_path.get(file_path) is None:
            continue
        if (file_path, type_name) in seen:
            continue
        seen.add((file_path, type_name))
        real_fields = _interface_field_names(contents, type_name)
        if real_fields:
            fixes.setdefault(file_path, []).append(
                f"Your data objects use a field called `{bad_field}`, but tsc says that "
                f"doesn't exist on the real `{type_name}` type (\"Object literal may only "
                f"specify known properties, and '{bad_field}' does not exist in type "
                f"'{type_name}'\"). The real `{type_name}` fields are exactly: "
                f"{real_fields}. Rename/adjust your data objects to use exactly these "
                f"field names - don't just delete `{bad_field}`, rename it to whichever "
                f"of {real_fields} it was meant to represent."
            )
        else:
            fixes.setdefault(file_path, []).append(
                f"Your data objects use a field called `{bad_field}`, but tsc says that "
                f"doesn't exist on the real `{type_name}` type. Check `{type_name}`'s real "
                f"declaration and rename this field to match it exactly."
            )
    return fixes


def _function_signature_mismatch_targets(tsc_output: str, plan: list[PlannedComponent]):
    """
    TS2322 + "Types of parameters 'X' and 'Y' are incompatible": a handler
    function passed as a prop has the WRONG signature - classically,
    writing a plain DOM-event handler (`(e: React.FormEvent) => void`)
    for a component that actually calls the callback with its own
    extracted data (`(data: {...}) => void`), not the raw event. The tsc
    message already contains both full signatures verbatim, so this
    needs no cross-file lookup - just quote them back precisely.
    """
    plan_by_path = {p.path: p for p in plan}
    fixes: dict[str, list[str]] = {}
    for file_path, actual_type, expected_type, _p1, _p2 in _FUNCTION_SIGNATURE_MISMATCH_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        if plan_by_path.get(file_path) is None:
            continue
        fixes.setdefault(file_path, []).append(
            f"A handler function you pass as a prop has the wrong signature. You wrote "
            f"a handler typed `{actual_type.strip()}`, but tsc says the real expected "
            f"type is `{expected_type.strip()}`. Rewrite the handler to match that exact "
            f"signature - use the parameter's own fields directly (it is NOT a raw DOM "
            f"event, so do not call `.preventDefault()` or access `.target` on it)."
        )
    return fixes


_NUMBER_NOT_STRING_RE = re.compile(
    r"src[/\\]([\w./\\-]+\.tsx)\(\d+,\d+\): error TS2322: Type 'number' is not assignable to type 'string'"
)
_ELEMENT_NOT_STRING_RE = re.compile(
    r"src[/\\]([\w./\\-]+\.tsx)\(\d+,\d+\): error TS2322: Type 'Element' is not assignable to type 'string'"
)


def _number_not_string_targets(tsc_output: str, plan: list[PlannedComponent]):
    """
    TS2322 "Type 'number' is not assignable to type 'string'" - a very
    common concrete cause: writing a price or similar value as a plain
    JS number (`3`) where the field is typed `string` (meant to hold
    something like `"$3"`). The bare message gives no field name to work
    from, so the note stays general but names the likely real cause
    directly instead of the generic undefined-value guidance, which
    doesn't describe this bug at all. Multiple occurrences in one file
    (e.g. one per menu item) are batched into a single note.
    """
    plan_by_path = {p.path: p for p in plan}
    fixes: dict[str, list[str]] = {}
    for file_path in _NUMBER_NOT_STRING_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        if plan_by_path.get(file_path) is None:
            continue
        if file_path in fixes:
            continue  # one combined note per file even if this repeats several times
        count = sum(1 for m in _NUMBER_NOT_STRING_RE.finditer(tsc_output) if m.group(1).replace("\\", "/") == file_path)
        occurrence_note = f" (this happens {count} times in this file)" if count > 1 else ""
        fixes[file_path] = [
            f"tsc reports \"Type 'number' is not assignable to type 'string'\"{occurrence_note}. "
            f"This almost always means a value (commonly a price) was written as a plain "
            f"JavaScript number (e.g. `3`) where the field's real type is `string` (meant "
            f"to hold something like `\"$3\"`). Find each such value and wrap it in quotes "
            f"as a string instead of a bare number."
        ]
    return fixes


def _element_not_string_targets(tsc_output: str, plan: list[PlannedComponent]):
    """
    TS2322 "Type 'Element' is not assignable to type 'string'" - a JSX
    element (e.g. `<span>...</span>`) was passed where a plain string
    prop is expected. Common cause: trying to add inline styling/markup
    to what's actually typed as plain text content.
    """
    plan_by_path = {p.path: p for p in plan}
    fixes: dict[str, list[str]] = {}
    for file_path in _ELEMENT_NOT_STRING_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        if plan_by_path.get(file_path) is None:
            continue
        fixes.setdefault(file_path, []).append(
            "tsc reports \"Type 'Element' is not assignable to type 'string'\" - somewhere "
            "you pass a JSX element (like `<span>...</span>`) where a plain string prop is "
            "expected. Extract the plain text content instead of passing rendered JSX "
            "markup for that prop."
        )
    return fixes


_REACT_DOM_UNKNOWN_EXPORT_RE = re.compile(
    r"src[/\\]([\w./\\-]+\.tsx)\(\d+,\d+\): error TS2305: Module '\"react-dom\"' has no "
    r"exported member '(\w+)'"
)


def _react_dom_unknown_export_targets(tsc_output: str, plan: list[PlannedComponent]):
    """
    TS2305: the model imported something from 'react-dom' that doesn't
    exist in this project's installed React version (18.3.1) - almost
    always `useFormState` / `useFormStatus`, newer/experimental
    form-action-related hooks the model may know from later React
    versions. This one hallucinated import typically cascades into
    several unrelated-looking downstream errors in the rest of the file
    (array-destructuring a plain object, wrong event-target types, etc.)
    as the rest of the code tries to use a hook that was never real here
    - so rather than trying to patch just the import line, this asks for
    a full rewrite of the file's form-handling logic using the standard
    React 18 pattern this project actually supports.
    """
    plan_by_path = {p.path: p for p in plan}
    names_by_path: dict[str, list[str]] = {}
    for file_path, name in _REACT_DOM_UNKNOWN_EXPORT_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        if plan_by_path.get(file_path) is None:
            continue
        names_by_path.setdefault(file_path, []).append(name)

    fixes: dict[str, list[str]] = {}
    for file_path, names in names_by_path.items():
        unique_names = list(dict.fromkeys(names))
        names_quoted = ", ".join(f"`{n}`" for n in unique_names)
        fixes[file_path] = [
            f"You import {names_quoted} from 'react-dom', but this project uses React "
            f"18.3.1, where these don't exist (tsc: \"Module 'react-dom' has no exported "
            f"member\"). These are newer/experimental form-action APIs this project "
            f"doesn't have. Rewrite this file's form state handling using standard React "
            f"18 patterns instead: `React.useState` for field values and submission "
            f"status, and a normal `onSubmit={{(e) => {{ e.preventDefault(); ... }}}}` "
            f"handler on the `<form>` - not `useFormState`/`useFormStatus` or "
            f"`<form action={{...}}>`. Any other type errors elsewhere in this same file "
            f"involving destructuring or event types are very likely fallout from this "
            f"same broken hook usage and should resolve once it's properly rewritten."
        ]
    return fixes


def _files_named_in_tsc_output(tsc_output: str, plan: list[PlannedComponent]) -> list[PlannedComponent]:
    """Map the file paths tsc printed in its error output back to plan entries."""
    named_paths = {m.replace("\\", "/") for m in _TSC_FILE_RE.findall(tsc_output)}
    return [p for p in plan if p.path in named_paths]


def _relative_import_path(from_path: str, to_path: str) -> str:
    """
    Compute the relative import specifier one planned file should use to
    import another, e.g. from "components/PricingPage.tsx" to
    "components/TierCard.tsx" -> "./TierCard"; from "App.tsx" to
    "components/TierCard.tsx" -> "./components/TierCard".
    """
    from_dir = Path(from_path).parent
    to_no_ext = Path(to_path).with_suffix("")
    rel = Path("/x") / to_no_ext  # anchor so relative_to below always works
    from_anchor = Path("/x") / from_dir
    try:
        rel_path = Path(
            __import__("os").path.relpath(str(rel), start=str(from_anchor))
        )
    except ValueError:
        rel_path = rel
    posix = rel_path.as_posix()
    if not posix.startswith("."):
        posix = "./" + posix
    return posix


_KNOWN_SHADCN_EXPORTS = {
    "Button": "@/components/ui/button",
    "Card": "@/components/ui/card",
    "CardHeader": "@/components/ui/card",
    "CardTitle": "@/components/ui/card",
    "CardDescription": "@/components/ui/card",
    "CardContent": "@/components/ui/card",
    "CardFooter": "@/components/ui/card",
    "Input": "@/components/ui/input",
}


def _missing_import_targets(tsc_output: str, plan: list[PlannedComponent]):
    """
    Recognize tsc's "Cannot find name 'X'" (TS2304) where X is either
    another planned component used in JSX but never imported, OR one of
    the shadcn sub-components (e.g. `CardFooter`) that IS actually
    available in this project but got left out of an existing
    `import { ... } from '@/components/ui/card'` line. Returns a dict of
    {file_path: correction_text} covering every such error found, so a
    single retry attempt can fix more than one forgotten import (in the
    same or different files) at once.
    """
    plan_by_component = {p.component_name: p for p in plan}
    plan_by_path = {p.path: p for p in plan}
    fixes: dict[str, list[str]] = {}
    for file_path, missing_name in _MISSING_IMPORT_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        caller = plan_by_path.get(file_path)
        if caller is None:
            continue
        owner = plan_by_component.get(missing_name)
        if owner is not None:
            import_path = _relative_import_path(caller.path, owner.path)
            fixes.setdefault(file_path, []).append(
                f"You use `<{missing_name}>` in this file's JSX but never import it, causing "
                f"a real tsc error (\"Cannot find name '{missing_name}'\"). Add this import "
                f"at the top of the file:\nimport {missing_name} from '{import_path}';"
            )
            continue
        shadcn_module = _KNOWN_SHADCN_EXPORTS.get(missing_name)
        if shadcn_module is not None:
            fixes.setdefault(file_path, []).append(
                f"You use `<{missing_name}>` but never import it (tsc: \"Cannot find name "
                f"'{missing_name}'\"). It IS one of the already-available shadcn components "
                f"in this project - add it to your import from '{shadcn_module}', e.g. "
                f"`import {{ ..., {missing_name} }} from '{shadcn_module}';`."
            )
            continue
        # Not one of our planned components and not a known shadcn export -
        # nothing we can confidently resolve, so leave it to the generic
        # fallback rather than guessing an import path.
    return fixes


def _unresolved_name_targets(tsc_output: str, plan: list[PlannedComponent]):
    """
    Catch-all for TS2304 "Cannot find name" that ISN'T a forgotten import
    of one of our own components or a known shadcn export (those are
    handled by _missing_import_targets above, which skips everything
    else). This residual case is almost always a genuine scope/typo bug,
    most commonly forgetting to go through the loop variable inside a
    `.map()` callback - e.g. writing `{price}` instead of `{item.price}`.
    The old generic fallback's correction text was written for "possibly
    undefined" tsc errors and doesn't describe this bug at all, so a
    small local model had little real guidance to fix it from.
    """
    plan_by_path = {p.path: p for p in plan}
    plan_by_component = {p.component_name: p for p in plan}
    fixes: dict[str, list[str]] = {}
    for file_path, name in _MISSING_IMPORT_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        if plan_by_path.get(file_path) is None:
            continue
        if plan_by_component.get(name) is not None or name in _KNOWN_SHADCN_EXPORTS:
            continue  # already handled by _missing_import_targets
        fixes.setdefault(file_path, []).append(
            f"You reference the bare identifier `{name}` somewhere in this file, but "
            f"tsc says it isn't defined anywhere (\"Cannot find name '{name}'\"). This "
            f"is almost always either a typo, or writing `{name}` when you meant a "
            f"property of some in-scope variable instead - most commonly inside a "
            f"`.map(item => ...)` callback, writing `{name}` directly instead of "
            f"`item.{name}`. Find that reference and fix it so it points at something "
            f"actually in scope."
        )
    return fixes


_UNAUTHORIZED_SHADCN_IMPORT_RE = re.compile(
    r"src[/\\]([\w./\\-]+\.tsx)\(\d+,\d+\): error TS2307: Cannot find module "
    r"'(@/components/ui/[\w-]+)' or its corresponding type declarations"
)


def _unauthorized_shadcn_import_targets(tsc_output: str, plan: list[PlannedComponent]):
    """
    TS2307: the file imports a shadcn path (e.g. '@/components/ui/textarea')
    that was never actually scaffolded in this project - only Button, the
    Card family, and Input really exist (per COMPONENT_USER_PROMPT_TEMPLATE).
    The model invented an import for a component the project doesn't have.
    Fix: remove that import and the JSX using it, and use a plain HTML
    element (styled with Tailwind) or one of the components that DO exist
    instead.
    """
    plan_by_path = {p.path: p for p in plan}
    available = ", ".join(sorted(set(_KNOWN_SHADCN_EXPORTS.values())))
    fixes: dict[str, list[str]] = {}
    for file_path, module_path in _UNAUTHORIZED_SHADCN_IMPORT_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        if plan_by_path.get(file_path) is None:
            continue
        fixes.setdefault(file_path, []).append(
            f"You import from '{module_path}', but that component was never actually "
            f"scaffolded in this project (tsc: \"Cannot find module '{module_path}'\"). "
            f"Only these shadcn modules really exist: {available}. Remove the import "
            f"and any JSX using it, and replace it with a plain HTML element styled "
            f"with Tailwind classes instead (e.g. a plain `<textarea>` for a text area)."
        )
    return fixes



def _missing_required_prop_targets(tsc_output: str, plan: list[PlannedComponent]):
    """
    Recognize tsc's "Property 'X' is missing in type '{}' but required in
    type '...Props'" (TS2741) - this happens when a caller renders a
    component without passing a prop that component's interface requires.
    Unlike an unknown EXTRA prop, the right fix here is to fix the
    CALLER (the file tsc actually points at) by passing real data for
    that prop, not to relax the child's interface to make it optional -
    doing that would silently hide a real missing feature (e.g. a
    pricing page rendered with no tier data at all).
    """
    plan_by_path = {p.path: p for p in plan}
    fixes: dict[str, list[str]] = {}
    for file_path, missing_prop, interface_name in _MISSING_REQUIRED_PROP_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        caller = plan_by_path.get(file_path)
        if caller is None:
            continue
        owner_name = interface_name[: -len("Props")] if interface_name.endswith("Props") else interface_name
        fixes.setdefault(file_path, []).append(
            f"You render `<{owner_name}>` without passing its required prop `{missing_prop}` "
            f"(tsc error: \"Property '{missing_prop}' is missing in type '{{}}' but required "
            f"in type '{interface_name}'\"). Add `{missing_prop}` with real, appropriate data "
            f"matching what `{owner_name}` needs - do not remove the prop requirement from "
            f"the child instead, since that would just hide missing content."
        )
    return fixes


def _react_umd_global_targets(tsc_output: str, plan: list[PlannedComponent]):
    """TS2686: the file uses the bare `React` identifier (e.g. `React.Fragment`,
    `React.ReactNode`) without ever importing it - fine under the classic JSX
    runtime's ambient global, but an error once the file is treated as an ES
    module. Fix: add `import React from 'react';`."""
    plan_by_path = {p.path: p for p in plan}
    fixes: dict[str, list[str]] = {}
    for file_path in _REACT_UMD_GLOBAL_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        if plan_by_path.get(file_path) is None:
            continue
        fixes.setdefault(file_path, []).append(
            "You reference the bare `React` identifier (e.g. `React.Fragment`, "
            "`React.ReactNode`) without importing it, causing a real tsc error "
            "(\"'React' refers to a UMD global, but the current file is a "
            "module\"). Add `import React from 'react';` at the top of the file."
        )
    return fixes


def _implicit_any_param_targets(tsc_output: str, plan: list[PlannedComponent]):
    """TS7006: a callback parameter (commonly in `.map(...)`) has no type
    annotation and TypeScript couldn't infer one - usually because the array
    it's iterating over itself ended up typed `any` from an earlier problem
    in the same file. Fix: give the parameter (and/or the array it comes
    from) an explicit type."""
    plan_by_path = {p.path: p for p in plan}
    fixes: dict[str, list[str]] = {}
    for file_path, param_name in _IMPLICIT_ANY_PARAM_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        if plan_by_path.get(file_path) is None:
            continue
        fixes.setdefault(file_path, []).append(
            f"The parameter `{param_name}` implicitly has type `any` (tsc: "
            f"\"Parameter '{param_name}' implicitly has an 'any' type\"). Give it "
            f"an explicit type annotation, or type the array/data it's derived "
            f"from so it's inferred correctly - do not leave it untyped or use "
            f"`any` explicitly."
        )
    return fixes


def _already_handled_required_prop_pairs(tsc_output: str) -> set[tuple[str, str]]:
    """
    (file_path, prop_name) pairs already covered by the two more specific
    required-prop detectors above, so the general catch-all below can
    skip exactly those and nothing else. Filtering has to happen at this
    per-(file, prop) granularity, not per-file: when one caller file is
    missing props for SEVERAL different child components, some of those
    mismatches match a specific detector and others only match the
    catch-all - skipping the catch-all's entire contribution for that
    file (as if "already handled" meant "nothing left to add here") was
    silently dropping the ones only the catch-all could see.
    """
    pairs: set[tuple[str, str]] = set()
    for file_path, prop, _interface in _MISSING_REQUIRED_PROP_RE.findall(tsc_output):
        pairs.add((file_path.replace("\\", "/"), prop))
    for file_path, _interface, props_csv in _MISSING_REQUIRED_PROPS_MULTI_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        for prop in props_csv.split(","):
            pairs.add((file_path, prop.strip()))
    return pairs


def _missing_property_any_targets(
    tsc_output: str, plan: list[PlannedComponent], already_handled: set[tuple[str, str]] | None = None
):
    """
    Catch-all for "Property 'X' is missing in type 'A' but required in type
    'B'" in whatever shape it appears (TS2322, TS2719, or a TS2741 whose
    required type is an inline object literal, not a plain interface name) -
    the narrower detectors above only match a subset of these (a literal
    empty-object caller, or a plain named "...Props" interface). The most
    common real cause: this file declares (or otherwise ends up with) its
    OWN local version of a type another component also uses, and the two
    have drifted out of sync - typically because a data literal here is
    missing a field the real component actually requires.

    already_handled, when given, is a set of (file_path, prop_name) pairs
    the more specific detectors already produced a note for - only those
    EXACT pairs are skipped, not the whole file, so a different missing
    prop in the same file (one only this catch-all can recognize) still
    gets through.
    """
    plan_by_path = {p.path: p for p in plan}
    already_handled = already_handled or set()
    fixes: dict[str, list[str]] = {}
    for file_path, missing_prop, required_type in _MISSING_PROPERTY_ANY_RE.findall(tsc_output):
        file_path = file_path.replace("\\", "/")
        if plan_by_path.get(file_path) is None:
            continue
        if (file_path, missing_prop) in already_handled:
            continue
        fixes.setdefault(file_path, []).append(
            f"Some data or a local type in this file is missing the property "
            f"`{missing_prop}`, but the actual required shape is `{required_type.strip()[:200]}` "
            f"(a real tsc type-mismatch error). If this file declares its own "
            f"local type that duplicates one from another component file, "
            f"either import and reuse that component's real exported type "
            f"instead of redeclaring your own, or add the missing "
            f"`{missing_prop}` field (with real data, not a placeholder) "
            f"everywhere this type is used."
        )
    return fixes



def _retry_component_with_notes(
    gateway, plan: list[PlannedComponent], target: PlannedComponent, description: str, notes: list[str]
) -> str:
    """Generic corrective retry: regenerate one file with a list of specific,
    plain-language corrections (forgotten imports, forgotten required props,
    etc.) appended, instead of just the raw tsc text."""
    plan_json = json.dumps(
        [{"path": p.path, "purpose": p.purpose, "exports": p.component_name} for p in plan], indent=2
    )
    correction = "IMPORTANT CORRECTIONS to your previous version of this file:\n" + "\n\n".join(
        f"- {note}" for note in notes
    )
    user_prompt = COMPONENT_USER_PROMPT_TEMPLATE.format(
        description=description.strip(),
        plan_json=plan_json,
        target_path=target.path,
        target_purpose=target.purpose,
        component_name=target.component_name,
    ) + "\n\n" + correction

    messages = [
        {"role": "system", "content": COMPONENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    raw = gateway.chat(messages, temperature=0.2, max_tokens=3000)
    tsx = _strip_fences(raw)
    if not _has_default_export(tsx):
        raise ValueError(f"{target.path}: corrective retry did not return a default-exported component. Got:\n{tsx[:400]}")
    return tsx


def _missing_prop_targets(tsc_output: str, plan: list[PlannedComponent]):
    """
    Recognize tsc's specific "Property 'X' does not exist on type
    '...&{Name}Props'" shape - this happens when a caller passes a prop
    a component's own interface doesn't declare. The right fix is almost
    always to ADD that prop to the OWNING component's interface (the
    caller's usage is deliberate - e.g. wiring up a click handler), not
    to regenerate the caller and silently strip the prop it was passing.
    `_files_named_in_tsc_output` alone would only find the call-site file
    (e.g. App.tsx) since that's where tsc points the line/col at, so this
    is checked first and, when it matches, takes priority over that.

    Uses finditer (not the first match only): a single build can have
    this same mismatch shape for MORE than one component at once (e.g.
    HeroSection missing one prop AND ContactForm missing a different
    one) - returning only the first would silently drop every other one,
    leaving it completely unfixed with no note ever reaching the model.

    Returns a list of (target_component, missing_prop_name, inferred_type),
    one per distinct (component, prop) pair found.
    """
    results = []
    seen = set()
    for m in _MISSING_PROP_RE.finditer(tsc_output):
        missing_prop, interface_name = m.group(1), m.group(2)
        target = next((p for p in plan if interface_name == f"{p.component_name}Props"), None)
        if target is None:
            continue
        key = (target.path, missing_prop)
        if key in seen:
            continue
        seen.add(key)
        # Recover the prop's real type from the object-literal type tsc printed
        # just before this message, e.g. "Type '{ ...; onSelect: () => void; }'
        # is not assignable to ...".
        type_m = re.search(rf"\b{re.escape(missing_prop)}\s*:\s*([^;{{}}]+?)\s*[;}}]", tsc_output)
        inferred_type = type_m.group(1).strip() if type_m else "unknown"
        results.append((target, missing_prop, inferred_type))
    return results


def _retry_component_with_missing_prop(
    gateway, plan: list[PlannedComponent], target: PlannedComponent, description: str,
    missing_prop: str, inferred_type: str, tsc_output: str,
) -> str:
    plan_json = json.dumps(
        [{"path": p.path, "purpose": p.purpose, "exports": p.component_name} for p in plan], indent=2
    )
    correction = (
        f"IMPORTANT CORRECTION: this component's caller passes a prop named "
        f"`{missing_prop}` (inferred type: `{inferred_type}`), but this "
        f"component's own props interface does not declare it, which caused "
        f"this real tsc error:\n{tsc_output.strip()[:800]}\n\n"
        f"Add `{missing_prop}: {inferred_type}` to this component's props "
        f"interface, destructure it, and actually wire it up (e.g. call it "
        f"from the relevant element's event handler if it's a function type) "
        f"- do not just drop or ignore it."
    )
    user_prompt = COMPONENT_USER_PROMPT_TEMPLATE.format(
        description=description.strip(),
        plan_json=plan_json,
        target_path=target.path,
        target_purpose=target.purpose,
        component_name=target.component_name,
    ) + "\n\n" + correction

    messages = [
        {"role": "system", "content": COMPONENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    raw = gateway.chat(messages, temperature=0.2, max_tokens=3000)
    tsx = _strip_fences(raw)
    if not _has_default_export(tsx):
        raise ValueError(f"{target.path}: missing-prop retry did not return a default-exported component. Got:\n{tsx[:400]}")
    return tsx


def _retry_component_with_runtime_error_ts(
    gateway, plan: list[PlannedComponent], target: PlannedComponent,
    description: str, runtime_event: dict, current_content: str,
) -> str:
    plan_json = json.dumps([{"path": p.path, "purpose": p.purpose, "exports": p.component_name} for p in plan], indent=2)
    diagnostic = "\n".join(
        f"{k}: {runtime_event.get(k)}" for k in ("message", "stack", "filename", "line", "column")
        if runtime_event.get(k)
    )
    correction = (
        "IMPORTANT RUNTIME REPAIR. The browser loaded the app but src/" + target.path +
        " threw a runtime error. Repair ONLY this component. Preserve the intended UI and props. "
        "Fix the concrete undefined/null/rendering fault shown below. Return the COMPLETE corrected raw .tsx file only.\n\n"
        f"Browser diagnostic:\n{diagnostic[:3000]}\n\nCurrent file:\nsrc/{target.path}\n{current_content[:12000]}"
    )
    user_prompt = COMPONENT_USER_PROMPT_TEMPLATE.format(
        description=description.strip(), plan_json=plan_json, target_path=target.path,
        target_purpose=target.purpose, component_name=target.component_name,
    ) + "\n\n" + correction
    raw = gateway.chat(
        [{"role": "system", "content": COMPONENT_SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
        temperature=0.15, max_tokens=4000,
    )
    tsx = _strip_fences(raw)
    if "export default" not in tsx:
        raise ValueError(f"{target.path}: runtime repair returned no default export")
    return tsx


def scaffold_react_ts_project(task_id: str, workspace_dir: str = "workspace") -> Path:
    """
    Real scaffold: copies the TS+shadcn template's config files, entry
    files, and the real shadcn/ui primitives (button/card/input) into a
    new project dir. node_modules is symlinked (falling back to a real
    copy if the OS blocks symlinks, e.g. Windows without admin/dev mode -
    same fix already proven for the plain React track).
    """
    import shutil

    if not TEMPLATE_DIR.exists():
        raise RuntimeError(f"React+TS template not found at {TEMPLATE_DIR}")
    if not (TEMPLATE_DIR / "node_modules").exists():
        import subprocess as _subprocess
        npm = shutil.which("npm")
        if npm is None:
            raise RuntimeError("npm was not found on PATH; install Node.js/npm so AZIZ can bootstrap React+TypeScript dependencies automatically")
        lock = TEMPLATE_DIR / "package-lock.json"
        cmd = [npm, "ci"] if lock.exists() else [npm, "install"]
        result = _subprocess.run(cmd, cwd=str(TEMPLATE_DIR), capture_output=True, text=True, timeout=240)
        if result.returncode != 0 or not (TEMPLATE_DIR / "node_modules").exists():
            detail = (result.stderr or result.stdout or "dependency installation failed")[-2500:]
            raise RuntimeError(f"Automatic React+TypeScript dependency bootstrap failed: {detail}")

    project_dir = Path(workspace_dir).resolve() / task_id.strip()
    (project_dir / "src" / "components" / "ui").mkdir(parents=True, exist_ok=True)
    (project_dir / "src" / "lib").mkdir(parents=True, exist_ok=True)

    for filename in TEMPLATE_FILES:
        shutil.copy(TEMPLATE_DIR / filename, project_dir / filename)
    for filename in TEMPLATE_SRC_FILES:
        shutil.copy(TEMPLATE_DIR / "src" / filename, project_dir / "src" / filename)
    for filename in TEMPLATE_UI_COMPONENTS:
        shutil.copy(TEMPLATE_DIR / "src" / "components" / "ui" / filename,
                    project_dir / "src" / "components" / "ui" / filename)
    shutil.copy(TEMPLATE_DIR / "src" / "lib" / "utils.ts", project_dir / "src" / "lib" / "utils.ts")

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


def run_typecheck(project_dir: Path, timeout: float = 60.0) -> list[str]:
    """
    The REAL, authoritative validator for TypeScript: actually run
    `npx tsc --noEmit` and read its real output. This catches genuine
    type errors that a per-file esbuild transform check cannot - most
    importantly, a component requiring a prop of a certain type that a
    caller never provides, or provides with the wrong type, becomes a
    real compiler error here instead of a silent runtime bug.
    """
    import shutil as _shutil

    npx = _shutil.which("npx")
    if npx is None:
        return ["npx not found on PATH - cannot run the real TypeScript type-check"]

    try:
        result = subprocess.run(
            [npx, "tsc", "--noEmit"],
            cwd=str(project_dir),
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return [f"tsc --noEmit timed out after {timeout}s"]

    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        return [f"TypeScript type-check failed:\n{output[:1500]}"]
    return []


def build_multi_component_react_ts_app(
    gateway, task_id: str, description: str, workspace_dir: str = "workspace", max_typecheck_attempts: int = 2
):
    """
    The full real chain: description -> plan -> each .tsx component
    generated (with real shadcn/ui primitives available) -> real
    prop-contract check + corrective retry -> real Vite dev server ->
    EVERY component individually validated against the real compiler ->
    a real `tsc --noEmit` type-check on the whole project, with a bounded
    corrective retry (feeding the real tsc error back to the model for
    whichever file it names) instead of surfacing a genuine type error
    as an unrecoverable build failure on the very first try.

    Returns (project_dir, port, process, plan, problems).
    """
    def emit(stage, message, **meta):
        if progress:
            progress(stage, message, **meta)

    emit("planning", "Planning React+TypeScript project structure")
    plan = generate_plan(gateway, description)
    contents = {}
    for planned in plan:
        emit("coding", f"Creating {planned.path}", file=planned.path)
        contents[planned.path] = generate_component(gateway, plan, planned, description)

    # Self-heal relative TSX imports before Vite/tsc.
    plan = validate_and_repair_imports(
        gateway, plan, contents, description, component_extension=".tsx"
    )

    mismatches = find_prop_contract_mismatches_detailed(plan, contents)
    plan_by_path = {p.path: p for p in plan}
    unresolved = []

    for mismatch in mismatches:
        target = plan_by_path[mismatch["path"]]

        if mismatch["caller_passes_nothing"]:
            fixed_any_caller = False
            for caller_path in mismatch["caller_paths"]:
                caller = plan_by_path.get(caller_path)
                if caller is None:
                    continue
                try:
                    contents[caller_path] = _retry_caller_with_missing_props(
                        gateway, plan, caller, description, mismatch["component_name"], mismatch["missing"]
                    )
                    fixed_any_caller = True
                except ValueError as exc:
                    unresolved.append(str(exc))
            if fixed_any_caller:
                recheck = find_prop_contract_mismatches_detailed(plan, contents)
                still_broken = next((m for m in recheck if m["path"] == mismatch["path"]), None)
                if still_broken:
                    unresolved.append(
                        f"{mismatch['path']}: still expects prop(s) {still_broken['missing']} "
                        f"even after fixing its caller(s)"
                    )
            continue

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
                f"{mismatch['path']}: still expects prop(s) {still_broken['missing']} "
                f"even after a corrective retry"
            )

    emit("scaffold", "Creating React+TypeScript project environment")
    project_dir = scaffold_react_ts_project(task_id, workspace_dir=workspace_dir)
    write_components(project_dir, plan, contents)
    _install_runtime_reporter(project_dir, task_id, runtime_token)

    emit("build", "Starting Vite and compiling React+TypeScript application")
    port = _free_port()
    port, process, startup_output = start_vite_dev_server_with_recovery(
        project_dir, port, progress=lambda kind, msg: emit(kind, msg)
    )
    # This track's template (shadcn/ui + Tailwind + TypeScript) has more
    # to cold-start and dependency-pre-bundle than the plain React
    # template validate_all_components' 15s default was tuned for, so it
    # gets a longer allowance here specifically rather than changing the
    # shared default for both tracks.
    vite_problems = validate_all_components(port, plan, process=process, timeout=35.0)
    if startup_output:
        emit("build", "Vite startup diagnostics captured", output=startup_output[-4000:])

    # A real Vite/esbuild parse failure (unclosed JSX tag, unbalanced
    # braces) can slip past _has_default_export AND a clean tsc pass -
    # tsc never sees this class of error since it's a Vite/esbuild-level
    # syntax failure, not a type error. Now that the message is parsed
    # into a clean one-liner (see _parse_vite_error_body), feed it back
    # for a bounded corrective retry.
    installed_dependencies = set()
    for _ in range(3):
        vite_failures = [p for p in vite_problems if ": Vite failed to compile" in p]
        if not vite_failures:
            break

        dependency_repaired = False
        dependency_remaining = []
        for failure in vite_failures:
            m_local = re.search(r'Failed to resolve import ["\']((?:\./|\../|@/)[^"\']+)["\'] from ["\'](?:src/)?([^"\']+)["\']', failure)
            if m_local:
                spec, importer_path = m_local.group(1), m_local.group(2).replace("\\", "/")
                try:
                    target, generated = _generate_missing_local_resource(
                        gateway, importer_path, spec, description, ".tsx", contents.get(importer_path, "")
                    )
                    contents[target] = generated
                    if not any(p.path == target for p in plan):
                        resource_name = Path(target).stem
                        if resource_name == "index":
                            resource_name = Path(target).parent.name or "Resource"
                        resource_name = re.sub(r"[^A-Za-z0-9]", "", resource_name.title()) or "Resource"
                        plan.append(PlannedComponent(target, f"Auto-created resource required by {importer_path}", resource_name))
                    emit("repair", f"Auto-created missing local resource {target}", file=target, resource=target)
                    dependency_repaired = True
                    continue
                except ValueError as exc:
                    emit("error", f"Automatic local resource creation failed for {spec}", error=str(exc))
            package_name = missing_dependency_from_vite_error(failure)
            if not package_name or package_name in installed_dependencies:
                dependency_remaining.append(failure)
                continue
            ok, detail = ensure_npm_dependency(project_dir, package_name, progress=lambda kind, msg, **meta: emit(kind, msg, **meta))
            if ok:
                installed_dependencies.add(package_name)
                dependency_repaired = True
            else:
                emit("error", f"Automatic dependency install failed for {package_name}", error=detail)
                dependency_remaining.append(failure)

        if dependency_repaired:
            write_components(project_dir, plan, contents)
            vite_problems = validate_all_components(port, plan, process=process, timeout=35.0)
            continue

        fixed_any = False
        remaining = []
        for failure in dependency_remaining:
            path = failure.split(":", 1)[0]
            target = plan_by_path.get(path)
            if target is None:
                remaining.append(failure)
                continue
            try:
                contents[path] = _retry_component_with_vite_error(gateway, plan, target, description, failure)
                fixed_any = True
            except ValueError as exc:
                remaining.append(str(exc))
        if not fixed_any:
            vite_problems = remaining + [p for p in vite_problems if ": Vite failed to compile" not in p]
            break
        write_components(project_dir, plan, contents)
        vite_problems = [p for p in vite_problems if ": Vite failed to compile" not in p] + validate_all_components(
            port, plan, process=process, timeout=35.0
        )

    problems = unresolved + vite_problems

    emit("typecheck", "Running TypeScript validation")
    typecheck_problems = run_typecheck(project_dir)
    for type_round in range(max_typecheck_attempts):
        emit("typecheck", f"TypeScript verification attempt {type_round + 1}", problems=typecheck_problems)
        if not typecheck_problems:
            break
        tsc_output = typecheck_problems[0]
        emit("error", "TypeScript errors found", error=tsc_output)

        # Gather EVERY recognizable fix across the whole tsc output first,
        # grouped by which file each one applies to - a single run can
        # (and here, does) contain more than one distinct, unrelated
        # error in different files, e.g. a forgotten import in one
        # component and a forgotten required prop in another. Batching
        # them into one attempt matters because max_typecheck_attempts
        # is bounded: handling only the first error per attempt could
        # exhaust the budget before every real issue is fixed.
        notes_by_path: dict[str, list[str]] = {}

        # A genuine syntax error (unterminated string, stray token, etc.)
        # invalidates everything tsc says about the REST of that file -
        # once the parser gets confused, every downstream "missing prop"
        # or "cannot find name" for the same file is noise, not a real
        # second bug. Check for this FIRST and, for any file that has
        # one, don't let other detectors add their (likely misleading)
        # notes for that same file this attempt.
        syntax_fixes = _syntax_error_targets(tsc_output, plan)
        for path, notes in syntax_fixes.items():
            notes_by_path.setdefault(path, []).extend(notes)
        syntax_broken_paths = set(syntax_fixes.keys())

        # Prefer fixing the component that actually OWNS a mismatched
        # interface (e.g. add the missing `onSelect` prop to
        # PricingCardProps) over regenerating whichever file tsc's
        # line/col happens to point at (often just the call site, which
        # would otherwise get "fixed" by silently dropping a prop the
        # caller was passing for a real reason). This one is handled
        # separately below since it needs the inferred type, not just a
        # plain-language note.
        missing_prop_fixes = _missing_prop_targets(tsc_output, plan)
        missing_prop_fixes = [f for f in missing_prop_fixes if f[0].path not in syntax_broken_paths]

        for path, notes in _missing_import_targets(tsc_output, plan).items():
            if path in syntax_broken_paths:
                continue
            notes_by_path.setdefault(path, []).extend(notes)
        for path, notes in _unresolved_name_targets(tsc_output, plan).items():
            if path in syntax_broken_paths:
                continue
            notes_by_path.setdefault(path, []).extend(notes)
        for path, notes in _unauthorized_shadcn_import_targets(tsc_output, plan).items():
            if path in syntax_broken_paths:
                continue
            notes_by_path.setdefault(path, []).extend(notes)
        for path, notes in _missing_required_prop_targets(tsc_output, plan).items():
            if path in syntax_broken_paths:
                continue
            notes_by_path.setdefault(path, []).extend(notes)
        for path, notes in _missing_required_props_multi_targets(tsc_output, plan).items():
            if path in syntax_broken_paths:
                continue
            notes_by_path.setdefault(path, []).extend(notes)
        for path, notes in _react_umd_global_targets(tsc_output, plan).items():
            if path in syntax_broken_paths:
                continue
            notes_by_path.setdefault(path, []).extend(notes)
        for path, notes in _implicit_any_param_targets(tsc_output, plan).items():
            if path in syntax_broken_paths:
                continue
            notes_by_path.setdefault(path, []).extend(notes)
        for path, notes in _named_import_should_be_default_targets(tsc_output, plan).items():
            if path in syntax_broken_paths:
                continue
            notes_by_path.setdefault(path, []).extend(notes)
        for path, notes in _object_literal_excess_prop_targets(tsc_output, plan, contents).items():
            if path in syntax_broken_paths:
                continue
            notes_by_path.setdefault(path, []).extend(notes)
        for path, notes in _function_signature_mismatch_targets(tsc_output, plan).items():
            if path in syntax_broken_paths:
                continue
            notes_by_path.setdefault(path, []).extend(notes)
        for path, notes in _number_not_string_targets(tsc_output, plan).items():
            if path in syntax_broken_paths:
                continue
            notes_by_path.setdefault(path, []).extend(notes)
        for path, notes in _element_not_string_targets(tsc_output, plan).items():
            if path in syntax_broken_paths:
                continue
            notes_by_path.setdefault(path, []).extend(notes)
        for path, notes in _react_dom_unknown_export_targets(tsc_output, plan).items():
            if path in syntax_broken_paths:
                continue
            notes_by_path.setdefault(path, []).extend(notes)
        # Catch-all last, and only for the SPECIFIC (file, prop) pairs the
        # more specific detectors above didn't already cover - filtering
        # at the whole-file level here would silently drop a different
        # missing prop in the same file that only this catch-all
        # recognizes (e.g. one caller missing required props for several
        # different child components, where only some of those mismatches
        # match a named "...Props" interface).
        already_handled_pairs = _already_handled_required_prop_pairs(tsc_output)
        for path, notes in _missing_property_any_targets(tsc_output, plan, already_handled_pairs).items():
            if path in syntax_broken_paths:
                continue
            notes_by_path.setdefault(path, []).extend(notes)

        fixed_any = False

        # Group by target path first: a single build can have this exact
        # mismatch shape for more than one component, but also more than
        # one missing prop for the SAME component - and retrying the same
        # file twice, once per prop, would have each call fully
        # regenerate it from scratch and silently undo the other prop's
        # fix. So each path gets exactly one combined retry.
        missing_prop_by_path: dict[str, list] = {}
        for fix in missing_prop_fixes:
            missing_prop_by_path.setdefault(fix[0].path, []).append(fix)

        for path, fixes_for_path in missing_prop_by_path.items():
            target = fixes_for_path[0][0]
            try:
                if len(fixes_for_path) == 1:
                    _, missing_prop, inferred_type = fixes_for_path[0]
                    contents[path] = _retry_component_with_missing_prop(
                        gateway, plan, target, description, missing_prop, inferred_type, tsc_output
                    )
                else:
                    combined_notes = [
                        f"Your component is missing the prop `{missing_prop}` (inferred "
                        f"type: `{inferred_type}`) that a caller passes to it. Add this "
                        f"prop to your Props interface and actually use it."
                        for _, missing_prop, inferred_type in fixes_for_path
                    ]
                    contents[path] = _retry_component_with_notes(gateway, plan, target, description, combined_notes)
                fixed_any = True
            except ValueError as exc:
                typecheck_problems = [str(exc)]
                break

        handled_paths = set(missing_prop_by_path.keys())
        for path, notes in notes_by_path.items():
            if path in handled_paths:
                continue
            target = plan_by_path.get(path)
            if target is None:
                continue
            try:
                contents[path] = _retry_component_with_notes(gateway, plan, target, description, notes)
                fixed_any = True
            except ValueError as exc:
                typecheck_problems = [str(exc)]
                break
        else:
            if fixed_any:
                write_components(project_dir, plan, contents)
                typecheck_problems = run_typecheck(project_dir)
                continue

        if fixed_any:
            # a ValueError broke out of the notes loop above - still
            # write whatever succeeded before stopping.
            write_components(project_dir, plan, contents)
            typecheck_problems = run_typecheck(project_dir)
            break

        # Nothing we specifically recognize - fall back to generic
        # per-file regeneration with the raw tsc text.
        targets = _files_named_in_tsc_output(tsc_output, plan)
        if not targets:
            break
        regenerated_any = False
        for target in targets:
            try:
                contents[target.path] = _retry_component_with_type_error(
                    gateway, plan, target, description, tsc_output
                )
                regenerated_any = True
            except ValueError as exc:
                typecheck_problems = [str(exc)]
        if not regenerated_any:
            break
        write_components(project_dir, plan, contents)
        typecheck_problems = run_typecheck(project_dir)

    problems += typecheck_problems

    # Browser runtime is the final authority for TSX too. A successful tsc
    # run does not prove that render-time values are defined or that a hook
    # is used legally. Reuse the same bounded targeted repair strategy as
    # plain React, but regenerate only the component named by the browser
    # diagnostic.
    if not problems and runtime_probe is not None:
        if runtime_status:
            runtime_status("verifying_runtime", 0, "Opening generated React+TypeScript app for runtime verification...", port=port, project_dir=str(project_dir))
        consumed_ready_seq = 0
        for repair_round in range(max(1, int(max_repairs)) + 1):
            deadline = __import__("time").time() + 25.0
            while __import__("time").time() < deadline:
                snapshot = runtime_probe() or {}
                errors = snapshot.get("errors") or []
                ready_seq = snapshot.get("ready_seq", 0)
                if errors or ready_seq > consumed_ready_seq:
                    break
                __import__("time").sleep(0.25)
            snapshot = runtime_probe() or {}
            errors = snapshot.get("errors") or []
            ready_seq = snapshot.get("ready_seq", 0)
            if not errors and ready_seq > consumed_ready_seq:
                if runtime_status:
                    runtime_status("done", repair_round, "Browser runtime verification passed: console is clean.", port=port, project_dir=str(project_dir))
                break
            if not errors:
                problems.append("Browser runtime verification timed out: no clean ready signal was received.")
                break
            if repair_round >= max(1, int(max_repairs)):
                problems.append("Browser runtime verification failed after the configured repair limit:\n" + "\n".join(str(e.get("message", e)) for e in errors[:8]))
                break
            event = errors[0]
            target_path = _runtime_target_path(plan, event)
            if target_path is None:
                problems.append("Browser runtime error could not be mapped to a single generated component:\n" + str(event))
                break
            target = next(p for p in plan if p.path == target_path)
            emit("error", f"Runtime error found in {target.path}", file=target.path, error=event)
            try:
                contents[target.path] = _retry_component_with_runtime_error_ts(
                    gateway, plan, target, description, event, contents[target.path]
                )
                (project_dir / "src" / target.path).write_text(contents[target.path], encoding="utf-8")
            except Exception as exc:
                problems.append(f"{target.path}: runtime repair failed: {exc}")
                break
            consumed_ready_seq = max(consumed_ready_seq, ready_seq)
            if runtime_status:
                runtime_status("repairing_runtime", repair_round + 1, f"Runtime error in {target.path}; repaired and retesting...", port=port, project_dir=str(project_dir))
        else:
            problems.append("Browser runtime verification did not reach a clean state.")

    return project_dir, port, process, plan, problems
