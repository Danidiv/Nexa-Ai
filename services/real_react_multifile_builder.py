"""
Real Multi-Component React Builder — extends real_react_builder.py the
same way real_multifile_builder.py extended real_frontend_builder.py:
a plan step first, then each component generated with the full plan as
context, so imports between components actually line up.

    description -> generate_plan()          (model call: JSON file list)
                 -> generate_component()     (model call per component)
                 -> write every file under src/
                 -> real Vite dev server
                 -> EVERY component fetched from it individually, so a
                    broken sub-component is caught even if App.jsx (the
                    entry point) itself is fine - a single HTTP GET only
                    transforms the ONE file requested, it does not follow
                    that file's imports, so each component must be
                    checked on its own to catch a hidden broken import.
"""
from __future__ import annotations

import json
import re
import time
import posixpath
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from services.plan_compression import replan_oversized_plan

from services.real_react_builder import (
    _strip_fences,
    _free_port,
    scaffold_react_project,
    start_vite_dev_server,
    start_vite_dev_server_with_recovery,
    vite_process_output,
    _parse_vite_error_body,
    ensure_npm_dependency,
    missing_dependency_from_vite_error,
)

PLAN_SYSTEM_PROMPT = (
    "You are a React project planner. Given an app description, output a "
    "JSON array (and NOTHING else - no markdown, no explanation) of the "
    "component files needed. Each item must have exactly these keys:\n"
    '  "path": relative path under src/, e.g. "App.jsx" or '
    '"components/PricingCard.jsx"\n'
    '  "purpose": one sentence describing what this component does\n'
    "Rules:\n"
    "- Exactly ONE item must have path exactly \"App.jsx\" - this is the "
    "entry component that main.jsx renders.\n"
    "- Every other item's path must start with \"components/\" and end "
    "in \".jsx\", with a PascalCase filename (e.g. components/PricingCard.jsx).\n"
    "- Keep it small: 2 to 10 files total, including App.jsx.\n"
    "- Output ONLY the JSON array."
)

COMPONENT_SYSTEM_PROMPT = (
    "You are a React component generator. Output ONLY raw .jsx file "
    "content - no markdown fences, no explanation."
)

COMPONENT_USER_PROMPT_TEMPLATE = (
    "Build this: {description}\n\n"
    "This project has these component files:\n{plan_json}\n\n"
    "Generate the COMPLETE content of ONE file: src/{target_path}\n"
    "What this component must do: {target_purpose}\n\n"
    "Requirements:\n"
    "- Export a single default function component named {component_name}.\n"
    "- Use Tailwind CSS utility classes for styling (already available on "
    "the page, no import needed) - do NOT write a <style> tag.\n"
    "- If this component needs another component from the list above, "
    "import it with its EXACT relative path from this file's location, "
    "using a default import, e.g.: "
    "import PricingCard from './components/PricingCard.jsx' (if this file "
    "is App.jsx) or import PricingCard from './PricingCard.jsx' (if this "
    "file is itself inside components/).\n"
    "- If this component renders MULTIPLE instances of the same child "
    "component side by side (e.g. several pricing tiers, several cards), "
    "arrange them with a Tailwind grid or flex layout - e.g. "
    "<div className=\"grid grid-cols-1 md:grid-cols-3 gap-6\"> - never let "
    "repeated items just stack full-width with no columns.\n"
    "- If a prop represents a price or currency amount, include the "
    "currency symbol in EXACTLY ONE place - either bake it into the prop "
    "value (e.g. price=\"$9.99\") or add it in the template (e.g. "
    "${{price}} with price=\"9.99\"), never both, or it will render as "
    "a doubled symbol like \"$$9.99\".\n"
    "- The pre-installed shadcn/ui components include Button, Card, Input, Label, and Badge at '@/components/ui/...'. Do NOT import a directory with a trailing slash such as '@/components/ui/'; use an explicit component path or '@/components/ui/index.jsx'. "
    "- Do NOT import any package other than 'react' and the shadcn "
    "components listed above. In particular, do NOT import react-router-dom, react-router, axios, lucide-react, @radix-ui packages, chart libraries, or any other npm package.\n"
    "- This is a plain JavaScript file (.jsx) - simple prop/state types are "
    "fine, but don't over-engineer types.\n"
    "- Output ONLY the raw .jsx file content."
)


@dataclass(frozen=True)
class PlannedComponent:
    path: str
    purpose: str
    component_name: str


def _component_name_from_path(path: str) -> str:
    stem = Path(path).stem
    if not re.match(r"^[A-Z][A-Za-z0-9]*$", stem):
        raise ValueError(f"component filename must be PascalCase: {path!r}")
    return stem


def generate_plan(gateway, description: str) -> list[PlannedComponent]:
    """Real plan call: ask the model for a small, valid component list."""
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
            gateway, description, items, entry_path='App.jsx', extension='.jsx'
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

        if path == "App.jsx":
            app_count += 1
        elif not (path.startswith("components/") and path.endswith(".jsx")):
            raise ValueError(f"invalid component path (must be App.jsx or components/*.jsx): {path!r}")

        component_name = _component_name_from_path(path)
        purpose = str(item.get("purpose", "")).strip()
        plan.append(PlannedComponent(path=path, purpose=purpose, component_name=component_name))

    if app_count != 1:
        raise ValueError(f"plan must contain exactly one App.jsx, found {app_count}")

    return plan


def _has_default_export(jsx: str) -> bool:
    """Accept `export { X as default }` too, not just the literal substring "export default"."""
    return bool(re.search(r"export\s+default\b", jsx)) or bool(
        re.search(r"export\s*\{[^}]*\bas\s+default\b[^}]*\}", jsx)
    )


def generate_component(
    gateway, plan: list[PlannedComponent], target: PlannedComponent, description: str, max_attempts: int = 2
) -> str:
    """Real per-component generation, with the full plan as context so imports line up."""
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

    last_jsx = ""
    for attempt in range(max_attempts):
        raw = gateway.chat(messages, temperature=0.2, max_tokens=3000)
        jsx = _strip_fences(raw)
        if _has_default_export(jsx):
            return jsx
        last_jsx = jsx
        messages = messages[:2] + [
            {"role": "assistant", "content": raw},
            {
                "role": "user",
                "content": (
                    "That response is missing a default export. Output ONLY "
                    f"the raw file content for src/{target.path}, and it MUST "
                    f"end with a line reading exactly:\n"
                    f"export default {target.component_name};\n"
                    "No markdown fences, no explanation, no other text."
                ),
            },
        ]

    raise ValueError(
        f"{target.path}: model did not return a default-exported component after "
        f"{max_attempts} attempts. Got:\n{last_jsx[:400]}"
    )


# Match relative imports AND the AZIZ/Vite `@/` alias.
_KNOWN_SCAFFOLD_UI = {
    "components/ui/badge.tsx",
    "components/ui/button.tsx",
    "components/ui/card.tsx",
    "components/ui/input.tsx",
    "components/ui/label.tsx",
    "components/ui/avatar.jsx",
    "components/ui/accordion.jsx",
}

_LOCAL_IMPORT_RE = re.compile(
    r"(?:import\s+(?:[^;\n]*?\s+from\s+)?|export\s+(?:[^;\n]*?\s+from\s+))"
    r"['\"](?P<spec>(?:\.{1,2}/|@/)[^'\"]+)['\"]"
)


def _resolve_local_import(importer: str, spec: str, available: set[str]) -> str | None:
    candidate = _local_spec_to_path(importer, spec, ".jsx")
    if candidate in available:
        return candidate
    base = candidate.rsplit(".", 1)[0] if candidate and "." in candidate else candidate
    for ext in ("jsx", "js", "tsx", "ts"):
        probe = f"{base}.{ext}"
        if probe in available:
            return probe
    for index_name in ("index.jsx", "index.js", "index.tsx", "index.ts"):
        probe = f"{base}/{index_name}"
        if probe in available:
            return probe
    return None


def _relative_import(from_path: str, target_path: str) -> str:
    """Return the exact ./ or ../ import path from one src file to another."""
    import posixpath
    spec = posixpath.relpath(target_path, posixpath.dirname(from_path) or ".")
    return spec if spec.startswith(".") else "./" + spec


def _rewrite_local_import(content: str, old: str, new: str) -> str:
    """Rewrite only quoted import/export specifiers, not arbitrary strings."""
    pattern = re.compile(r"(['\"])" + re.escape(old) + r"\1")
    return pattern.sub(lambda m: m.group(1) + new + m.group(1), content)



def _normalize_directory_import_spec(spec: str, target: str) -> str:
    """Make a trailing-slash directory import point at an explicit index module."""
    target = target.replace("\\", "/").lstrip("./")
    return "@/" + target if spec.startswith("@/") else "./" + target

def _scaffold_ui_index_content() -> str:
    """Deterministic barrel for UI primitives already copied by the scaffold."""
    return """export { Badge, badgeVariants } from './badge.tsx';
export { Button, buttonVariants } from './button.tsx';
export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent } from './card.tsx';
export { Input } from './input.tsx';
export { Label } from './label.tsx';
export { Avatar, AvatarImage, AvatarFallback } from './avatar.jsx';
export { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from './accordion.jsx';
"""

def _local_spec_to_path(importer: str, spec: str, extension: str = ".jsx") -> str | None:
    """Map a React local/alias import to a normalized src-relative path.

    Directory imports such as ``@/components/ui/`` resolve to an index file,
    not to ``components/ui.jsx``. Relative paths containing ``..`` are also
    normalized so ``./components/../ActivityTable`` becomes
    ``components/ActivityTable`` instead of creating a bogus duplicate file.
    """
    if spec.startswith("@/"):
        candidate = spec[2:].replace("\\", "/").lstrip("/")
    elif spec.startswith("./") or spec.startswith("../"):
        candidate = posixpath.join(posixpath.dirname(importer), spec.replace("\\", "/"))
    else:
        return None
    is_directory_import = spec.endswith("/")
    candidate = posixpath.normpath(candidate).lstrip("/")
    if is_directory_import or candidate in (".", ""):
        return posixpath.join(candidate.rstrip("/"), "index" + extension)
    p = Path(candidate)
    if p.suffix:
        return p.as_posix()
    return p.with_suffix(extension).as_posix()


def _imported_symbols(content: str, spec: str) -> list[str]:
    """Best-effort extraction of imported names so generated resources export the right symbols."""
    names: list[str] = []
    pattern = re.compile(r'import\s+(.+?)\s+from\s+["\']' + re.escape(spec) + r'["\']', re.DOTALL)
    m = pattern.search(content)
    if not m:
        return names
    clause = m.group(1).strip()
    if clause.startswith("{") and "}" in clause:
        inside = clause[1:clause.rfind("}")]
        for item in inside.split(","):
            raw = item.strip()
            if not raw:
                continue
            name = raw.split(" as ")[-1].strip()
            if re.fullmatch(r"[A-Za-z_$][\w$]*", name):
                names.append(name)
    else:
        default = clause.split(",", 1)[0].strip()
        if re.fullmatch(r"[A-Za-z_$][\w$]*", default):
            names.append("default:" + default)
    return names


_DETERMINISTIC_UI_RESOURCES = {
    "components/ui/avatar.jsx": """import React from 'react';

export const Avatar = React.forwardRef(({ className = '', children, ...props }, ref) => (
  <span ref={ref} className={`inline-flex h-10 w-10 shrink-0 overflow-hidden rounded-full bg-muted ${className}`} {...props}>
    {children}
  </span>
));
Avatar.displayName = 'Avatar';

export const AvatarImage = React.forwardRef(({ src, alt = '', className = '', ...props }, ref) => (
  <img ref={ref} src={src} alt={alt} className={`aspect-square h-full w-full object-cover ${className}`} {...props} />
));
AvatarImage.displayName = 'AvatarImage';

export const AvatarFallback = React.forwardRef(({ children, className = '', ...props }, ref) => (
  <span ref={ref} className={`flex h-full w-full items-center justify-center rounded-full bg-muted text-sm font-medium ${className}`} {...props}>
    {children}
  </span>
));
AvatarFallback.displayName = 'AvatarFallback';
""",
    "components/ui/accordion.jsx": """import React, { useState } from 'react';

export const Accordion = ({ children, className = '', ...props }) => (
  <div className={className} {...props}>{children}</div>
);

export const AccordionItem = ({ children, className = '', ...props }) => (
  <div className={`border-b ${className}`} {...props}>{children}</div>
);

export const AccordionTrigger = ({ children, className = '', ...props }) => {
  const [open, setOpen] = useState(false);
  return (
    <button type='button' className={`flex w-full items-center justify-between py-4 text-left font-medium ${className}`} onClick={() => setOpen(v => !v)} {...props}>
      <span>{children}</span><span aria-hidden='true'>{open ? '−' : '+'}</span>
    </button>
  );
};

export const AccordionContent = ({ children, className = '', ...props }) => (
  <div className={`pb-4 text-sm text-muted-foreground ${className}`} {...props}>{children}</div>
);
""",
}


def _generate_missing_local_resource(gateway, importer: str, spec: str, description: str, extension: str = ".jsx", importer_content: str | None = None) -> tuple[str, str]:
    """Generate a missing local resource from the actual import contract."""
    target = _local_spec_to_path(importer, spec, extension)
    if not target:
        raise ValueError(f"cannot resolve local resource {spec!r}")
    symbols = _imported_symbols(importer_content if importer_content is not None else _LAST_CONTENTS_FOR_RESOURCE.get(importer, ""), spec)
    target_name = Path(target).stem
    is_ui = target.startswith("components/ui/")
    deterministic = _DETERMINISTIC_UI_RESOURCES.get(target)
    if deterministic:
        requested_named = [s for s in symbols if not s.startswith("default:")]
        if requested_named and not all(_has_named_export(deterministic, symbol) for symbol in requested_named):
            raise ValueError(f"deterministic UI resource {target} cannot satisfy requested exports: {requested_named}")
        return target, deterministic
    if is_ui:
        prompt = (
            f"Create the missing React UI module src/{target}. The importing file is src/{importer} "
            f"and imports {symbols or ['the module']}. Build small reusable accessible UI primitives. "
            "Export named symbols exactly matching the requested imports; if a default import is requested, "
            "also export a default component. Use React and Tailwind only. "
            "IMPORTANT: this is a plain JavaScript .jsx file, NEVER use TypeScript syntax such as "
            "interfaces, type annotations, generic parameters, `as Type`, or `: string`/`: ReactNode`. "
            "No markdown."
        )
    else:
        prompt = (
            f"Create the missing local React resource src/{target}. It is imported by src/{importer} "
            f"from {spec!r}. Requested exports: {symbols or ['infer from the import']}. "
            f"Project description: {description}. Produce a complete valid {extension} file. "
            "Match the requested named/default exports exactly. Use only necessary dependencies and do not import unknown packages. "
            "For .jsx output, this MUST be plain JavaScript: no TypeScript interfaces, type annotations, generics, `as Type`, "
            "or other TypeScript syntax. No markdown."
        )
    messages = [
        {"role": "system", "content": "You generate missing local React project resources. Output ONLY the raw file content."},
        {"role": "user", "content": prompt},
    ]
    last_content = ""
    for attempt in range(2):
        raw = gateway.chat(messages, temperature=0.15, max_tokens=2200)
        content = _strip_fences(raw)
        last_content = content
        if not content.strip():
            continue
        requested_named = [s for s in symbols if not s.startswith("default:")]
        missing_requested = [s for s in requested_named if not _has_named_export(content, s)]
        if extension == ".jsx" and (re.search(r"(?:^|[({,]\s*)[A-Za-z_$][\w$]*\s*:\s*(?:string|number|boolean|ReactNode|any|unknown)\b|\binterface\s+[A-Za-z_$]|\btype\s+[A-Za-z_$].*=|\bas\s+[A-Za-z_$][\w$]*(?:\[\])?", content) or missing_requested):
            reason = "The output contained TypeScript syntax. Rewrite it as plain JavaScript JSX." if not missing_requested else ("The output did not export these named symbols: " + ", ".join(missing_requested) + ". Add them exactly.")
            messages = messages + [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": reason + " Output ONLY the corrected file content. Keep every requested named/default export."},
            ]
            continue
        return target, content
    raise ValueError(f"model returned invalid content for missing resource {target}: {last_content[:400]}")


def _has_named_export(content: str, symbol: str) -> bool:
    """Best-effort check that a generated JS module really exports a named symbol."""
    if not re.fullmatch(r"[A-Za-z_$][\w$]*", symbol or ""):
        return False
    patterns = [
        rf"\bexport\s+(?:const|let|var|function|class)\s+{re.escape(symbol)}\b",
        rf"\bexport\s*\{{[^}}]*\b{re.escape(symbol)}\b[^}}]*\}}",
    ]
    return any(re.search(pattern, content, re.DOTALL) for pattern in patterns)


def _missing_named_export_from_vite_error(problem: str) -> tuple[str, str] | None:
    """Extract (module path, symbol) from Vite's missing named-export diagnostic."""
    m = re.search(
        r"requested module ['\"](?P<module>[^'\"]+)['\"] does not provide an export named ['\"](?P<symbol>[A-Za-z_$][\w$]*)['\"]",
        problem,
        re.IGNORECASE,
    )
    if not m:
        return None
    module = m.group("module").replace("\\", "/")
    module = module.split("?", 1)[0].split("#", 1)[0]
    if module.startswith("/src/"):
        module = module[5:]
    elif module.startswith("src/"):
        module = module[4:]
    return module, m.group("symbol")


def _repair_missing_named_export(
    gateway, module_path: str, symbol: str, importer_path: str,
    importer_content: str, module_content: str, description: str, extension: str = ".jsx"
) -> str:
    """Repair a local module's export contract without consuming a normal code-repair round."""
    type_rule = (
        "This is a plain JavaScript .jsx module. Do NOT use TypeScript syntax, type aliases, interfaces, "
        "generic parameters, `as Type`, or type annotations."
        if extension == ".jsx" else
        "Preserve valid TypeScript syntax appropriate for this .tsx module."
    )
    prompt = f"""A generated React module has an export-contract error.

Importer: src/{importer_path}
Importer code:
{importer_content[:9000]}

Module that must provide the export: src/{module_path}
Current module code:
{module_content[:12000]}

Missing named export: {symbol}
Project description: {description}

Repair ONLY the module above. Preserve all existing useful exports and UI behavior, and add/repair the named export `{symbol}` so the importer can legally import it. If the symbol is a UI primitive, implement the smallest sensible primitive matching how the importer uses it. Do not invent unrelated dependencies or files. {type_rule}
Output ONLY the complete corrected raw file content, no markdown."""
    raw = gateway.chat(
        [{"role": "system", "content": "You repair local React module export contracts. Output only raw file content."},
         {"role": "user", "content": prompt}],
        temperature=0.12, max_tokens=3200,
    )
    content = _strip_fences(raw)
    if not content.strip() or not _has_named_export(content, symbol):
        raise ValueError(f"{module_path}: repair did not produce named export {symbol}")
    if extension == ".jsx" and re.search(r"\binterface\s+[A-Za-z_$]|\btype\s+[A-Za-z_$].*=|:\s*(?:string|number|boolean|ReactNode|any|unknown)\b|\bas\s+[A-Za-z_$][\w$]*(?:\[\])?", content):
        raise ValueError(f"{module_path}: repair returned TypeScript syntax in a .jsx file")
    return content


_LAST_CONTENTS_FOR_RESOURCE: dict[str, str] = {}


def resolve_missing_local_resources(gateway, plan, contents, description: str, max_resources: int = 8, extension: str = ".jsx") -> int:
    """Create missing local/alias resources before spending an LLM code-repair attempt."""
    created = 0
    global _LAST_CONTENTS_FOR_RESOURCE
    _LAST_CONTENTS_FOR_RESOURCE = contents
    try:
        for importer, content in list(contents.items()):
            for match in list(_LOCAL_IMPORT_RE.finditer(content)):
                spec = match.group("spec")
                candidate = _local_spec_to_path(importer, spec, extension)
                if not candidate:
                    continue
                available = set(contents) | _KNOWN_SCAFFOLD_UI
                if candidate in available or any(
                    p.rsplit(".", 1)[0] == candidate.rsplit(".", 1)[0] for p in available if "." in p
                ):
                    continue
                # A unique existing basename is repaired deterministically by
                # the validation pass; do not spend an LLM call generating a
                # duplicate component.
                stem = Path(candidate).stem
                basename_matches = [p for p in available if Path(p).stem == stem]
                if len(basename_matches) == 1:
                    continue
                if created >= max_resources:
                    raise ValueError(f"missing local resources exceeded automatic creation limit ({max_resources})")
                target = _local_spec_to_path(importer, spec, extension)
                if target == "components/ui/index.jsx":
                    generated = _scaffold_ui_index_content()
                else:
                    target, generated = _generate_missing_local_resource(
                        gateway, importer, spec, description, extension,
                        importer_content=content
                    )
                contents[target] = generated
                created += 1
                if not any(p.path == target for p in plan):
                    resource_name = Path(target).stem
                    if resource_name == "index":
                        resource_name = Path(target).parent.name or "Resource"
                    resource_name = re.sub(r"[^A-Za-z0-9]", "", resource_name.title()) or "Resource"
                    plan.append(PlannedComponent(target, f"Auto-created resource required by {importer}", resource_name))
        return created
    finally:
        _LAST_CONTENTS_FOR_RESOURCE = {}


def validate_and_repair_imports(
    gateway,
    plan: list[PlannedComponent],
    contents: dict[str, str],
    description: str,
    max_rounds: int = 3,
    component_extension: str = ".jsx",
) -> list[PlannedComponent]:
    """Self-heal generated relative imports before Vite starts.

    Wrong paths are fixed deterministically when a unique planned file has
    the same basename. Missing component imports are promoted into the plan
    and generated, bounded to prevent unbounded model expansion.
    """
    max_files = 8
    for _round in range(max_rounds):
        available = set(contents) | _KNOWN_SCAFFOLD_UI
        changed = False
        created_resources = resolve_missing_local_resources(gateway, plan, contents, description, max_resources=8, extension=component_extension)
        if created_resources:
            changed = True
            available = set(contents) | _KNOWN_SCAFFOLD_UI
        missing: list[tuple[str, str, str]] = []

        for path, content in list(contents.items()):
            for match in list(_LOCAL_IMPORT_RE.finditer(content)):
                spec = match.group("spec")
                resolved_target = _resolve_local_import(path, spec, available)
                if resolved_target:
                    if spec.endswith("/"):
                        explicit = _normalize_directory_import_spec(spec, resolved_target)
                        new_content = _rewrite_local_import(contents[path], spec, explicit)
                        if new_content != contents[path]:
                            contents[path] = new_content
                            changed = True
                    continue

                stem = Path(spec).name
                if not Path(stem).suffix:
                    stem += component_extension
                basename_matches = [p for p in available if Path(p).name == stem]
                if len(basename_matches) == 1:
                    corrected = _relative_import(path, basename_matches[0])
                    new_content = _rewrite_local_import(contents[path], spec, corrected)
                    if new_content != contents[path]:
                        contents[path] = new_content
                        changed = True
                    continue

                candidate = (Path(path).parent / spec).as_posix().lstrip("./")
                candidate_path = Path(candidate)
                if candidate_path.suffix == "" and candidate_path.name:
                    candidate_path = candidate_path.with_suffix(component_extension)
                candidate = candidate_path.as_posix()
                if candidate.startswith("components/") and candidate.endswith(component_extension):
                    missing.append((path, spec, candidate))

        unique_missing = []
        seen_missing = set()
        for item in missing:
            if item[2] not in seen_missing:
                seen_missing.add(item[2])
                unique_missing.append(item)

        if unique_missing:
            if len(plan) + len(unique_missing) > max_files:
                raise ValueError(
                    f"generated React project needs more than {max_files} components "
                    "after import repair; refusing unbounded model expansion"
                )
            plan_paths = {p.path for p in plan}
            for caller_path, spec, candidate in unique_missing:
                if candidate in plan_paths:
                    continue
                component_name = _component_name_from_path(candidate)
                purpose = (
                    f"Reusable component required by {caller_path} via local import "
                    f"{spec}; infer its UI from the overall project description."
                )
                target = PlannedComponent(candidate, purpose, component_name)
                plan.append(target)
                contents[candidate] = generate_component(gateway, plan, target, description)
                plan_paths.add(candidate)
                changed = True

        if not changed:
            return plan

    available = set(contents) | _KNOWN_SCAFFOLD_UI
    unresolved = []
    for path, content in contents.items():
        for match in _LOCAL_IMPORT_RE.finditer(content):
            spec = match.group("spec")
            if _resolve_local_import(path, spec, available) is None:
                unresolved.append(f"{path}: unresolved local import {spec!r}")
    if unresolved:
        raise ValueError("Import validation failed after self-repair:\n" + "\n".join(unresolved))
    return plan


def write_components(project_dir: Path, plan: list[PlannedComponent], contents: dict[str, str]) -> None:
    """Real files, real paths, under project_dir/src/."""
    src_dir = project_dir / "src"
    for planned in plan:
        content = contents.get(planned.path)
        if content is None:
            raise ValueError(f"missing generated content for {planned.path}")
        file_path = src_dir / planned.path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")


def _resolve_existing_local_module(contents: dict[str, str], importer: str, spec: str) -> str | None:
    """Resolve a local/alias import against the in-memory generated files."""
    target = _local_spec_to_path(importer, spec, ".jsx")
    if not target:
        return None
    candidates = [target]
    p = Path(target)
    if p.suffix:
        candidates.extend([p.with_suffix(".js").as_posix(), p.with_suffix(".tsx").as_posix(), p.with_suffix(".ts").as_posix()])
    else:
        candidates.extend([target + ext for ext in (".jsx", ".js", ".tsx", ".ts")])
    candidates.append(posixpath.join(target, "index.jsx"))
    candidates.append(posixpath.join(target, "index.js"))
    candidates.append(posixpath.join(target, "index.tsx"))
    candidates.append(posixpath.join(target, "index.ts"))
    for candidate in candidates:
        candidate = posixpath.normpath(candidate).lstrip("/")
        if candidate in contents:
            return candidate
    return None


def _local_import_contract_errors(contents: dict[str, str]) -> list[tuple[str, str, str, str]]:
    """Return local import/export mismatches as (importer, target, kind, symbol)."""
    errors: list[tuple[str, str, str, str]] = []
    import_re = re.compile(r'import\s+([\s\S]*?)\s+from\s+["\']([^"\']+)["\']\s*;?')
    for importer, content in contents.items():
        if not isinstance(content, str):
            continue
        for match in import_re.finditer(content):
            clause, spec = match.group(1).strip(), match.group(2)
            if not (spec.startswith("@/") or spec.startswith("./") or spec.startswith("../")):
                continue
            target = _resolve_existing_local_module(contents, importer, spec)
            if not target:
                continue
            target_content = contents.get(target, "")
            if clause.startswith("{"):
                inside = clause[1:clause.rfind("}")] if "}" in clause else clause[1:]
                for item in inside.split(","):
                    item = item.strip()
                    if not item:
                        continue
                    imported = item.split(" as ", 1)[0].strip()
                    if re.fullmatch(r"[A-Za-z_$][\w$]*", imported) and not _has_named_export(target_content, imported):
                        errors.append((importer, target, "named", imported))
            elif clause and not clause.startswith("*"):
                default_name = clause.split(",", 1)[0].strip()
                if re.fullmatch(r"[A-Za-z_$][\w$]*", default_name) and not _has_default_export(target_content):
                    errors.append((importer, target, "default", default_name))
    return errors


def validate_all_components(port: int, plan: list[PlannedComponent], process=None, timeout: float = 45.0) -> list[str]:
    """Validate generated React files against the real Vite dev server.

    Vite transforms modules asynchronously. On Windows, several sequential
    urllib requests can occasionally hit a socket read timeout even though
    the dev server is healthy. Treat those transport timeouts as *soft*
    validation warnings and let the browser-runtime gate make the final
    decision. Real HTTP 4xx/5xx Vite compiler responses remain hard failures.

    Requests are also made concurrently and localhost/127.0.0.1 are both
    tried to avoid Windows loopback resolution issues.
    """
    problems = []

    def _get(url: str, request_timeout: float = 8.0):
        return urllib.request.urlopen(url, timeout=request_timeout)

    # Wait for the server itself. Use both common Windows loopback addresses.
    deadline = time.time() + timeout
    server_ready = False
    last_error = None
    first_path = plan[0].path
    while time.time() < deadline:
        if process is not None and process.poll() is not None:
            break
        for host in ("127.0.0.1", "localhost"):
            try:
                with _get(f"http://{host}:{port}/src/{first_path}", 3) as resp:
                    resp.read()
                server_ready = True
                break
            except urllib.error.HTTPError:
                # HTTP response proves the server is alive; compile failure is
                # handled in the per-file pass below.
                server_ready = True
                break
            except Exception as exc:
                last_error = exc
        if server_ready:
            break
        time.sleep(0.25)

    if not server_ready:
        if process is not None:
            if process.poll() is not None:
                return [
                    f"Vite startup failed on port {port} (process exited, code {process.returncode}).\n"
                    f"{vite_process_output(process) or 'No Vite stdout/stderr was captured.'}"
                ]
            return [
                f"Dev server on port {port} never became reachable within {timeout}s. "
                f"Last probe error: {last_error}"
            ]
        return [f"Dev server on port {port} never became reachable within {timeout}s"]

    def validate_one(planned: PlannedComponent):
        last_timeout = None
        for host in ("127.0.0.1", "localhost"):
            try:
                with _get(f"http://{host}:{port}/src/{planned.path}", 8) as resp:
                    resp.read()
                return None
            except urllib.error.HTTPError as exc:
                body = exc.read().decode(errors="replace")
                summary = _parse_vite_error_body(body)
                return f"{planned.path}: Vite failed to compile (HTTP {exc.code}): {summary}"
            except TimeoutError as exc:
                last_timeout = exc
            except Exception as exc:
                # Windows/urllib can surface socket timeouts through several
                # wrapper exception types. Any clearly identified timeout is
                # transport noise, not a React compile failure.
                reason = getattr(exc, "reason", None)
                timeout_text = " ".join(
                    str(value).lower()
                    for value in (exc, reason)
                    if value is not None
                )
                if (
                    isinstance(exc, TimeoutError)
                    or isinstance(reason, TimeoutError)
                    or "timed out" in timeout_text
                    or "timeout" in timeout_text
                    or "timedout" in timeout_text
                ):
                    last_timeout = exc
                else:
                    return f"{planned.path}: request failed: {exc}"
        if last_timeout is not None:
            # Soft failure: the browser runtime gate is authoritative and will
            # catch an actual module/runtime failure. Do not abort the whole
            # build merely because this individual probe lost its socket.
            return None
        return None

    # Per-module HTTP probes are early diagnostics only. Browser runtime
    # verification is authoritative, so transport timeouts must never become
    # hard build failures.
    # Parallel probes avoid a slow module starving later modules on Windows.
    with ThreadPoolExecutor(max_workers=min(6, max(1, len(plan)))) as pool:
        futures = {pool.submit(validate_one, planned): planned for planned in plan}
        for future in as_completed(futures):
            result = future.result()
            if result:
                problems.append(result)

    # Preserve plan order for deterministic logs/tests.
    order = {p.path: i for i, p in enumerate(plan)}
    problems.sort(key=lambda item: order.get(item.split(":", 1)[0], 9999))
    return problems


def _split_top_level(s: str) -> list[str]:
    """Split a destructuring pattern's inner text on commas, but only at
    bracket depth 0 - so a default value like `items = [1, 2]` or
    `style = { a: 1 }` doesn't get split into extra bogus entries."""
    parts, current, depth = [], [], 0
    for ch in s:
        if ch in "{[(":
            depth += 1
        elif ch in "}])":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current))
    return parts


def extract_destructured_props(jsx_content: str, component_name: str) -> set[str]:
    """
    Real, if limited, static check: find this component's own function
    signature and extract the prop names it destructures, e.g.
    `function TierCard({ tierName, price })` -> {'tierName', 'price'}.
    Returns an empty set if no destructuring pattern is found (e.g. the
    component uses `props.x` style, or takes no props) - callers should
    treat an empty set as "can't determine", not "takes no props".

    Each comma-separated entry is parsed properly rather than just
    grabbing every `\\w+` token in the braces: a default value
    (`highlighted = false`) used to have its VALUE ("false") picked up
    as if it were a separate prop name, and a rename
    (`price: cost`) used to report the local alias ("cost") instead of
    the actual prop key the caller has to pass ("price").
    """
    patterns = [
        rf"function\s+{re.escape(component_name)}\s*\(\s*\{{((?:[^{{}}]|\{{[^{{}}]*\}})*)\}}",
        rf"{re.escape(component_name)}\s*=\s*\(\s*\{{((?:[^{{}}]|\{{[^{{}}]*\}})*)\}}",
    ]
    for pattern in patterns:
        m = re.search(pattern, jsx_content)
        if m:
            props = set()
            for segment in _split_top_level(m.group(1)):
                segment = segment.strip()
                if not segment or segment.startswith("..."):
                    continue  # rest element - not a specific named prop
                segment = segment.split("=", 1)[0].strip()  # drop `= default`
                segment = segment.split(":", 1)[0].strip()  # `price: alias` -> `price`
                if re.match(r"^\w+$", segment):
                    props.add(segment)
            return props
    return set()


def extract_props_passed(caller_content: str, component_name: str) -> set[str] | None:
    """
    Real check: find every <ComponentName ...> usage in a file and
    collect every prop name passed across all of them.

    Returns None instead of a set when a usage spreads props in rather
    than passing them as literal attributes (`<X {...headerProps} />`)
    and the spread can't be confidently resolved. Previously a spread
    usage was invisible to this check entirely, so every prop the
    component legitimately destructured looked "missing" - which then
    fed the corrective retry FALSE information ("the caller passes
    none of these props"), and the model would obediently rewrite the
    component's real prop interface to drop fields the caller was
    actually still passing, turning a false positive into a genuine
    tsc error.
    """
    passed = set()
    saw_unresolved_spread = False
    for m in re.finditer(rf"<{re.escape(component_name)}\b([^>]*)/?>", caller_content):
        attrs_text = m.group(1)
        passed |= set(re.findall(r"(\w+)\s*=(?!=)", attrs_text))
        for spread_m in re.finditer(r"\{\s*\.\.\.\s*(\w+|\{[^{}]*\})\s*\}", attrs_text):
            token = spread_m.group(1)
            if token.startswith("{"):
                # inline object literal spread: {...{ title: "...", description: "..." }}
                passed |= set(re.findall(r"(\w+)\s*:", token))
                continue
            # spread of a named variable - try to resolve its shape from
            # a `const NAME = { ... }` (optionally typed) earlier in the
            # same file; only give up (and flag "can't determine") if
            # that declaration isn't found.
            obj_m = re.search(
                rf"(?:const|let|var)\s+{re.escape(token)}\s*(?::[^=]+)?=\s*"
                rf"\{{((?:[^{{}}]|\{{[^{{}}]*\}})*)\}}",
                caller_content,
            )
            if obj_m:
                passed |= set(re.findall(r"(\w+)\s*:", obj_m.group(1)))
            else:
                saw_unresolved_spread = True
    if saw_unresolved_spread:
        return None
    return passed


def find_prop_contract_mismatches_detailed(plan: list[PlannedComponent], contents: dict[str, str]) -> list[dict]:
    """
    Same real check as find_prop_contract_mismatches(), but returns
    structured data instead of formatted strings, so a corrective retry
    can be built from it: exactly which props this component wrongly
    expects, and exactly which props its real caller(s) actually pass.

    Also reports which caller file(s) render this component and whether
    ANY of them pass it a single relevant prop. That distinction decides
    which side of the mismatch actually needs to change: if the caller
    passes some props but under different names, the child's naming is
    the more likely typo. But if the caller passes this component NO
    props at all, the child's prop design (title/subtitle, etc.) is
    usually the sensible one - the real bug is the caller never wiring
    real content through - and rewriting the child to drop props it
    clearly needs just to satisfy this check would make things worse.
    """
    results = []
    for planned in plan:
        if planned.path == "App.jsx":
            continue

        destructured = extract_destructured_props(contents[planned.path], planned.component_name)
        if not destructured:
            continue

        passed_anywhere = set()
        caller_paths = set()
        undetermined = False
        for other_path, other_content in contents.items():
            if other_path == planned.path:
                continue
            if f"<{planned.component_name}" in other_content:
                caller_paths.add(other_path)
            props_here = extract_props_passed(other_content, planned.component_name)
            if props_here is None:
                undetermined = True
                continue
            passed_anywhere |= props_here

        if not caller_paths or undetermined:
            continue

        missing = destructured - passed_anywhere
        if missing:
            results.append({
                "path": planned.path,
                "component_name": planned.component_name,
                "missing": sorted(missing),
                "actually_passed": sorted(passed_anywhere),
                "caller_paths": sorted(caller_paths),
                "caller_passes_nothing": not passed_anywhere,
            })
    return results


def find_prop_contract_mismatches(plan: list[PlannedComponent], contents: dict[str, str]) -> list[str]:
    """
    Real check for a real bug class: a child component destructures a
    prop name that NO caller ever actually passes - usually because the
    parent uses a different name for the same concept (e.g. parent passes
    `title`, child expects `tierName`). This is valid JavaScript (the prop
    is just silently undefined), so Vite's compiler can't catch it - only
    checking the actual prop names used on both sides can.

    Deliberately conservative: if a component's destructuring pattern
    can't be found (e.g. it uses `props.x` instead), or it's never used
    anywhere in the plan, it's skipped rather than risking a false
    positive - same philosophy as the DOM-reference checker for the
    plain-JS track.
    """
    detailed = find_prop_contract_mismatches_detailed(plan, contents)
    return [
        f"{d['path']}: expects prop(s) {d['missing']} but no caller ever "
        f"passes them by that name - likely a naming mismatch with the caller"
        for d in detailed
    ]


def _retry_component_with_correction(
    gateway, plan: list[PlannedComponent], target: PlannedComponent, description: str, mismatch: dict
) -> str:
    """
    Real, targeted retry: tell the model EXACTLY which prop names its
    caller(s) actually pass, and require it to use those exact names.
    This is much more specific than a generic "try again" - it hands the
    model the real ground truth instead of hoping it guesses right twice.
    """
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
    jsx = _strip_fences(raw)
    if not _has_default_export(jsx):
        raise ValueError(f"{target.path}: retry did not return a default-exported component. Got:\n{jsx[:400]}")
    return jsx


def _retry_caller_with_missing_props(
    gateway, plan: list[PlannedComponent], caller: PlannedComponent, description: str,
    callee_name: str, missing_props: list[str],
) -> str:
    """
    The mirror image of _retry_component_with_correction: used when a
    child component is rendered with NO relevant props at all, even
    though it clearly destructures and uses some. In that case the
    child's design is the sensible one and the caller is what's actually
    incomplete, so this regenerates the CALLER instead - telling it to
    pass real, appropriate data for the props the child needs, rather
    than gutting the child's interface to match an empty call site.
    """
    plan_json = json.dumps(
        [{"path": p.path, "purpose": p.purpose, "exports": p.component_name} for p in plan], indent=2
    )
    correction = (
        f"IMPORTANT CORRECTION: your previous version of this file renders "
        f"`<{callee_name}>` without passing it any of the prop(s) it actually "
        f"needs: {missing_props}. Keep rendering `<{callee_name}>`, but pass "
        f"real, appropriate content for {missing_props} this time - do not "
        f"render it with no props."
    )
    user_prompt = COMPONENT_USER_PROMPT_TEMPLATE.format(
        description=description.strip(),
        plan_json=plan_json,
        target_path=caller.path,
        target_purpose=caller.purpose,
        component_name=caller.component_name,
    ) + "\n\n" + correction

    messages = [
        {"role": "system", "content": COMPONENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    raw = gateway.chat(messages, temperature=0.2, max_tokens=3000)
    jsx = _strip_fences(raw)
    if not _has_default_export(jsx):
        raise ValueError(f"{caller.path}: caller retry did not return a default-exported component. Got:\n{jsx[:400]}")
    return jsx


def _retry_component_with_vite_error(
    gateway, plan: list[PlannedComponent], target: PlannedComponent, description: str, vite_message: str
) -> str:
    """
    Corrective retry for a REAL Vite/esbuild compile failure (unclosed
    JSX tag, unbalanced braces, truncated output, etc.) - the one class
    of bug _has_default_export can't catch, since a file can contain
    "export default" and still be otherwise malformed. vite_message is
    the parsed one-line summary from _parse_vite_error_body, not the raw
    HTML error page.
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
    jsx = _strip_fences(raw)
    if not _has_default_export(jsx):
        raise ValueError(f"{target.path}: vite-error retry did not return a default-exported component. Got:\n{jsx[:400]}")
    return jsx


def _runtime_target_path(plan: list[PlannedComponent], event: dict) -> str | None:
    """Map a browser runtime error to exactly one generated component."""
    text = "\n".join(str(event.get(k, "")) for k in ("message", "stack", "filename", "component"))
    for planned in plan:
        if planned.path in text or planned.path.replace("\\", "/") in text:
            return planned.path
    for planned in plan:
        if re.search(rf"\bat\s+{re.escape(planned.component_name)}(?:\s|\(|$)", text):
            return planned.path
        if re.search(rf"\b{re.escape(Path(planned.path).stem)}\.jsx(?::|\b)", text):
            return planned.path
    return None


def _retry_component_with_runtime_error(
    gateway, plan: list[PlannedComponent], target: PlannedComponent,
    description: str, runtime_event: dict, current_content: str,
) -> str:
    """Targeted runtime repair: regenerate ONLY the component that crashed."""
    plan_json = json.dumps(
        [{"path": p.path, "purpose": p.purpose, "exports": p.component_name} for p in plan], indent=2
    )
    diagnostic = "\n".join(
        f"{k}: {runtime_event.get(k)}" for k in ("message", "stack", "filename", "line", "column")
        if runtime_event.get(k)
    )
    correction = (
        "IMPORTANT RUNTIME REPAIR. The browser successfully loaded the app, but "
        f"src/{target.path} threw a runtime error. Repair ONLY this component. "
        "Do not change imports or invent files unless they are already in the plan. "
        "Preserve the intended UI and public props. Remove the specific undefined/null "
        "access or other runtime fault shown by the diagnostic.\n\n"
        f"Browser diagnostic:\n{diagnostic[:3000]}\n\n"
        f"Current failing file:\nsrc/{target.path}\n{current_content[:10000]}\n\n"
        "Return the COMPLETE corrected raw .jsx file and nothing else."
    )
    user_prompt = COMPONENT_USER_PROMPT_TEMPLATE.format(
        description=description.strip(), plan_json=plan_json,
        target_path=target.path, target_purpose=target.purpose,
        component_name=target.component_name,
    ) + "\n\n" + correction
    raw = gateway.chat(
        [{"role": "system", "content": COMPONENT_SYSTEM_PROMPT},
         {"role": "user", "content": user_prompt}],
        temperature=0.15, max_tokens=3500,
    )
    jsx = _strip_fences(raw)
    if not _has_default_export(jsx):
        raise ValueError(f"{target.path}: runtime-repair response has no default export")
    return jsx


def _install_runtime_reporter(project_dir: Path, task_id: str, runtime_token: str | None = None) -> None:
    """Inject a tiny browser-side runtime/console reporter into index.html."""
    index = project_dir / "index.html"
    html = index.read_text(encoding="utf-8")
    marker = "<!-- AZIZ_RUNTIME_REPORTER -->"
    if marker in html:
        return
    script = r"""
<!-- AZIZ_RUNTIME_REPORTER -->
<script>
(function() {
  const taskId = __AZIZ_TASK_ID__;
  const runtimeToken = __AZIZ_RUNTIME_TOKEN__;
  const parentRef = document.referrer;
  let endpoint = null;
  try { endpoint = parentRef ? new URL(parentRef).origin + '/api/runtime-errors/' + encodeURIComponent(taskId) : null; } catch (_) {}
  // Do not abort reporting when the preview has no referrer (for example,
  // when the generated app is opened directly). Parent postMessage is still
  // a valid transport and is the authoritative UI-side channel.
  const sent = new Set();
  let hadError = false;
  let runtimeState = 'loading';
  function clean(v) { try { return typeof v === 'string' ? v : JSON.stringify(v); } catch (_) { return String(v); } }
  function report(type, data) {
    const payload = Object.assign({type, task_id: taskId, runtime_token: runtimeToken, url: location.href, ts: Date.now()}, data || {});
    const key = type + '|' + clean(payload.message) + '|' + clean(payload.stack);
    if (type === 'error' && sent.has(key)) return;
    if (type === 'error') { sent.add(key); hadError = true; }
    const body = JSON.stringify(payload);
    let delivered = false;
    if (endpoint) {
      try {
        const blob = new Blob([body], {type: 'text/plain;charset=UTF-8'});
        if (navigator.sendBeacon) delivered = navigator.sendBeacon(endpoint + (runtimeToken ? ('?runtime_token=' + encodeURIComponent(runtimeToken)) : ''), blob);
      } catch (_) {}
      if (!delivered) {
        try {
          fetch(endpoint + (runtimeToken ? ('?runtime_token=' + encodeURIComponent(runtimeToken)) : ''), {method:'POST', mode:'cors', credentials:'include', keepalive:true, headers:{'Content-Type':'text/plain;charset=UTF-8', 'X-AZIZ-Runtime-Token': runtimeToken || ''}, body}).then(function(){}, function(){});
          delivered = true;
        } catch (_) {}
      }
    }
    // Always forward runtime evidence to the authenticated AZIZ parent UI as
    // well. A direct fetch can return 401/404 or appear delivered without
    // actually reaching the task endpoint (for example when the preview is
    // on a different Vite origin). The parent is the authoritative transport.
    if (window.parent && window.parent !== window) {
      try { window.parent.postMessage({type:'AZIZ_RUNTIME_REPORT', payload:payload}, '*'); } catch (_) {}
    }
  }
  function markRuntimeState(state, message, detail) {
    try {
      runtimeState = state;
      document.documentElement.setAttribute('data-aziz-runtime', state);
      if (message) document.documentElement.setAttribute('data-aziz-runtime-message', String(message).slice(0, 1000));
      if (detail) document.documentElement.setAttribute('data-aziz-runtime-detail', String(detail).slice(0, 1600));
    } catch (_) {}
  }
  window.addEventListener('error', function(e) {
    const msg = e.message || 'Unknown window error';
    const filename = e.filename || '';
    const line = e.lineno || 0;
    const column = e.colno || 0;
    const detail = [filename, line ? ('line ' + line) : '', column ? ('column ' + column) : ''].filter(Boolean).join(' ');
    markRuntimeState('error', msg, detail);
    report('error', {message: msg, stack: e.error && e.error.stack || '', filename, line, column, component: ''});
  });
  window.addEventListener('unhandledrejection', function(e) {
    const r = e.reason;
    const message = r && r.message ? r.message : clean(r);
    markRuntimeState('error', message);
    report('error', {message, stack: r && r.stack || '', filename:'', line:0, column:0, component:''});
  });
  window.addEventListener('message', function(e) {
    if (!e || !e.data || e.data.type !== 'AZIZ_RUNTIME_PING') return;
    if (runtimeState === 'ready') {
      report('ready', {message:'browser runtime ready (parent handshake)'});
    } else if (runtimeState === 'error') {
      report('error', {message: document.documentElement.getAttribute('data-aziz-runtime-message') || 'browser runtime error'});
    }
  });
  const originalConsoleError = console.error;
  console.error = function() {
    const args = Array.prototype.slice.call(arguments);
    const message = args.map(clean).join(' ');
    if (/uncaught|cannot read properties|is not defined|is not a function|invalid hook|maximum update|rendered more hooks|element type is invalid|failed to/i.test(message)) {
      report('error', {message, stack: new Error().stack || '', filename:'', line:0, column:0, component:''});
    }
    originalConsoleError.apply(console, arguments);
  };
  setTimeout(function() {
    if (!hadError) {
      markRuntimeState('ready', 'browser runtime settled with no actionable console errors');
      report('ready', {message:'browser runtime settled with no actionable console errors'});
    }
  }, 1500);
})();
</script>
"""
    script = script.replace('__AZIZ_TASK_ID__', json.dumps(task_id)).replace('__AZIZ_RUNTIME_TOKEN__', json.dumps(runtime_token or ''))
    html = html.replace('</head>', script + '</head>', 1)
    index.write_text(html, encoding='utf-8')



def _headless_browser_smoke_test(port: int, timeout: float = 12.0) -> tuple[bool, str]:
    """Verify the generated app with a real local Chromium when the UI reporter is unavailable."""
    import os
    import shutil
    import subprocess
    browser = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
    if browser is None and os.name == "nt":
        for candidate in (
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        ):
            if candidate and Path(candidate).exists():
                browser = candidate
                break
    if browser is None:
        return False, "No Chromium/Chrome browser executable is available for fallback verification."
    url = f"http://127.0.0.1:{int(port)}/?aziz_headless_verify=1"
    profile = Path(__file__).resolve().parent.parent / ".aziz_headless_profiles"
    profile.mkdir(parents=True, exist_ok=True)
    run_profile = profile / f"run_{int(time.time()*1000)}"
    cmd = [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", f"--user-data-dir={run_profile}", "--virtual-time-budget=4000", "--dump-dom", url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        dom = result.stdout or ""
        stderr = (result.stderr or "")[-3000:]
        match = re.search(r'<html[^>]*data-aziz-runtime=["\\\']([^"\\\']+)["\\\'][^>]*', dom, re.I)
        state = match.group(1).lower() if match else ""
        if state == "ready":
            return True, "Headless Chromium runtime verification passed: browser reporter reached ready state."
        if state == "error":
            msg = re.search(r'data-aziz-runtime-message=["\\\']([^"\\\']*)["\\\']', dom, re.I)
            detail = msg.group(1) if msg else "browser reported an actionable runtime error"
            return False, f"Headless Chromium detected a runtime error: {detail}"
        if result.returncode != 0:
            return False, f"Chromium exited with code {result.returncode}. {stderr}".strip()
        return False, "Chromium loaded the page but no AZIZ runtime ready/error marker was observed."
    except subprocess.TimeoutExpired:
        return False, "Headless Chromium verification timed out while loading the generated app."
    finally:
        shutil.rmtree(run_profile, ignore_errors=True)


def build_multi_component_react_app(gateway, task_id: str, description: str, workspace_dir: str = "workspace", runtime_probe=None, runtime_status=None, progress=None, max_repairs: int = 5, runtime_token: str | None = None):
    """
    The full real chain: description -> plan -> each component generated
    -> real prop-contract check -> ONE corrective retry per mismatched
    component, using the real caller's actual prop names as ground truth
    -> all written under src/ -> real Vite dev server -> EVERY component
    individually validated against the real compiler.

    Returns (project_dir: Path, port: int, process: Popen, plan: list[PlannedComponent], problems: list[str]).
    """
    def emit(stage, message, **meta):
        if progress:
            progress(stage, message, **meta)

    emit("planning", "Planning project structure")
    plan = generate_plan(gateway, description)
    emit("planning", f"Plan created: {len(plan)} files", files=[p.path for p in plan])
    contents = {}
    for planned in plan:
        emit("coding", f"Creating {planned.path}", file=planned.path)
        contents[planned.path] = generate_component(gateway, plan, planned, description)

    emit("imports", "Checking imports and missing components")
    plan = validate_and_repair_imports(gateway, plan, contents, description)
    emit("imports", "Import validation completed", files=[p.path for p in plan])

    # Prop-contract analysis is advisory for JavaScript/JSX. A child may
    # legitimately define optional props (callbacks, labels, feature flags,
    # etc.) that a particular caller does not pass. Treating every missing
    # prop name as a build blocker caused false failures such as an
    # ActivityTable expecting optional `onFiltersChange`. Real failures are
    # caught by Vite/Babel and browser runtime verification. Keep the analysis
    # for diagnostics, but never consume an LLM repair attempt or mark an
    # otherwise compilable project as failed.
    mismatches = find_prop_contract_mismatches_detailed(plan, contents)
    unresolved = []
    if mismatches:
        for mismatch in mismatches:
            emit(
                "build",
                f"Prop contract advisory: {mismatch['path']} may expect optional prop(s) "
                f"{mismatch['missing']}; continuing to real build/runtime verification",
                file=mismatch["path"],
                props=mismatch["missing"],
                callers=mismatch["caller_paths"],
            )

    emit("scaffold", "Creating React project environment")
    project_dir = scaffold_react_project(task_id, workspace_dir=workspace_dir)
    write_components(project_dir, plan, contents)
    _install_runtime_reporter(project_dir, task_id, runtime_token)

    emit("build", "Starting Vite and compiling generated application")
    port = _free_port()
    port, process, startup_output = start_vite_dev_server_with_recovery(
        project_dir, port, progress=lambda kind, msg: emit(kind, msg)
    )
    vite_problems = validate_all_components(port, plan, process=process, timeout=45.0)
    if startup_output:
        emit("build", "Vite startup diagnostics captured", output=startup_output[-4000:])
    emit("build", "Initial Vite validation completed", problems=vite_problems)

    # Vite's own parser is the real syntax check nothing else in this
    # pipeline performs (having "export default" somewhere, per
    # _has_default_export, says nothing about whether the REST of the
    # file is well-formed - an unclosed JSX tag or unbalanced brace still
    # passes that check and only shows up here). Now that the error
    # message is a clean, parsed one-liner instead of a raw HTML page,
    # feed it back for a bounded corrective retry, same pattern as every
    # other error class in this pipeline.
    installed_dependencies = set()
    invalid_dependencies: set[str] = set()
    seen_vite_failures: dict[str, int] = {}
    # Deterministic resource/dependency recovery gets its own generous budget.
    # These rounds do NOT represent LLM code-repair attempts.
    for compile_round in range(1, 8):
        emit("build", f"Build verification attempt {compile_round}")
        # Validate generated local import/export contracts in-memory. Vite can
        # return 200 for a module by itself even though an importing module
        # later fails on a missing named export. Catch that deterministically
        # before browser runtime so the resolver can repair the correct file.
        contract_repaired = False
        for importer_path, module_path, kind, symbol in _local_import_contract_errors(contents):
            if kind != "named":
                continue
            try:
                contents[module_path] = _repair_missing_named_export(
                    gateway, module_path, symbol, importer_path, contents.get(importer_path, ""),
                    contents[module_path], description, ".jsx"
                )
                emit("repair", f"Repaired missing named export {symbol} in {module_path}", file=module_path, export=symbol)
                contract_repaired = True
            except ValueError as exc:
                emit("error", f"Automatic export-contract repair failed for {module_path}", file=module_path, error=str(exc))
        if contract_repaired:
            write_components(project_dir, plan, contents)
            vite_problems = validate_all_components(port, plan, process=process)
            continue
        vite_failures = [p for p in vite_problems if ": Vite failed to compile" in p]
        if not vite_failures:
            break

        # First repair missing npm packages deterministically. This is a
        # dependency/environment problem, not a code-generation problem, so
        # it MUST NOT consume an LLM repair attempt. npm may detach the
        # scaffold's shared node_modules symlink and create a project-local
        # node_modules when it needs to add the package.
        dependency_repaired = False
        dependency_remaining = []
        for failure in vite_failures:
            # Missing named export from an already-existing local module is a
            # resource-contract problem. Repair that module first, without
            # consuming the normal component/code repair budget.
            named_export = _missing_named_export_from_vite_error(failure)
            if named_export:
                module_path, symbol = named_export
                module_path = module_path.lstrip("/")
                if module_path.startswith("src/"):
                    module_path = module_path[4:]
                importer_match = re.search(r"from ['\"](?:src/)?([^'\"]+)['\"]", failure)
                importer_path = importer_match.group(1).replace("\\", "/") if importer_match else ""
                if module_path in contents:
                    try:
                        importer_content = contents.get(importer_path, "")
                        contents[module_path] = _repair_missing_named_export(
                            gateway, module_path, symbol, importer_path, importer_content,
                            contents[module_path], description, ".jsx"
                        )
                        emit("repair", f"Repaired missing named export {symbol} in {module_path}", file=module_path, export=symbol)
                        dependency_repaired = True
                        continue
                    except ValueError as exc:
                        emit("error", f"Automatic export-contract repair failed for {module_path}", file=module_path, error=str(exc))

            m_local = re.search(r'Failed to resolve import ["\']((?:\./|\../|@/)[^"\']+)["\'] from ["\'](?:src/)?([^"\']+)["\']', failure)
            if m_local:
                spec, importer_path = m_local.group(1), m_local.group(2)
                importer_path = importer_path.replace("\\", "/")
                try:
                    target, generated = _generate_missing_local_resource(
                        gateway, importer_path, spec, description, ".jsx",
                        importer_content=contents.get(importer_path, "")
                    )
                    contents[target] = generated
                    if not any(p.path == target for p in plan):
                        resource_name = Path(target).stem
                        if resource_name == "index":
                            resource_name = Path(target).parent.name or "Resource"
                        resource_name = re.sub(r"[^A-Za-z0-9]", "", resource_name.title()) or "Resource"
                        plan.append(PlannedComponent(target, f"Auto-created resource required by {importer_path}", resource_name))
                    emit("repair", f"Auto-created missing local resource {target}", file=target, resource=target)
                    write_components(project_dir, plan, contents)
                    plan_by_path = {p.path: p for p in plan}
                    dependency_repaired = True
                    continue
                except ValueError as exc:
                    emit("error", f"Automatic local resource creation failed for {spec}", error=str(exc))
            package_name = missing_dependency_from_vite_error(failure)
            if not package_name or package_name in installed_dependencies:
                dependency_remaining.append(failure)
                continue
            if package_name in invalid_dependencies:
                dependency_remaining.append(failure)
                continue
            ok, detail = ensure_npm_dependency(project_dir, package_name, progress=lambda kind, msg, **meta: emit(kind, msg, **meta))
            if ok:
                installed_dependencies.add(package_name)
                dependency_repaired = True
            else:
                if str(detail).startswith("INVALID_NPM_PACKAGE:"):
                    invalid_dependencies.add(package_name)
                    emit("error", f"Invalid npm package detected: {package_name}; switching to code repair", file=failure.split(":", 1)[0], error=detail)
                else:
                    emit("error", f"Automatic dependency install failed for {package_name}", file=failure.split(":", 1)[0], error=detail)
                dependency_remaining.append(failure)

        if dependency_repaired:
            write_components(project_dir, plan, contents)
            vite_problems = validate_all_components(port, plan, process=process)
            continue

        fixed_any = False
        remaining = []
        for _failure in dependency_remaining:
            seen_vite_failures[_failure] = seen_vite_failures.get(_failure, 0) + 1
        plan_by_path = {p.path: p for p in plan}
        for failure in dependency_remaining:
            path = failure.split(":", 1)[0]
            emit("error", f"Build error found in {path}", file=path, error=failure)
            target = plan_by_path.get(path)
            if target is None:
                remaining.append(failure)
                continue
            try:
                emit("repair", f"Fixing {path}", file=path, error=failure)
                repair_failure = failure
                package_name = missing_dependency_from_vite_error(failure)
                if package_name in invalid_dependencies:
                    repair_failure += (
                        f"\n\nThe imported npm package {package_name!r} was verified unavailable from npm (404/ETARGET). "
                        "Do NOT retry installing it. Replace/remove that import using an existing dependency or a small local implementation. "
                        "Keep the requested UI behavior and do not introduce another unverified package."
                    )
                if seen_vite_failures.get(failure, 0) >= 2:
                    repair_failure += "\n\nThis exact diagnostic has repeated. Change recovery strategy instead of repeating the same import/dependency fix."
                contents[path] = _retry_component_with_vite_error(gateway, plan, target, description, repair_failure)
                fixed_any = True
                emit("repair", f"Patched {path}", file=path)
            except ValueError as exc:
                remaining.append(str(exc))
        if not fixed_any:
            vite_problems = remaining + [p for p in vite_problems if ": Vite failed to compile" not in p]
            break
        write_components(project_dir, plan, contents)
        vite_problems = [p for p in vite_problems if ": Vite failed to compile" not in p] + validate_all_components(
            port, plan, process=process
        )

    problems = unresolved + vite_problems
    if not problems and runtime_probe is not None:
        if runtime_status:
            runtime_status("verifying_runtime", 0, "Opening generated app in the browser for runtime verification...", port=port, project_dir=str(project_dir))
        max_repairs = max(1, int(max_repairs))
        revision = 0
        consumed_ready_seq = 0
        for repair_round in range(max_repairs + 1):
            deadline = time.time() + 25.0
            snapshot = None
            while time.time() < deadline:
                snapshot = runtime_probe() or {}
                errors = snapshot.get("errors") or []
                ready_seq = snapshot.get("ready_seq", 0)
                if errors or ready_seq > consumed_ready_seq:
                    break
                time.sleep(0.25)
            snapshot = runtime_probe() or {}
            errors = snapshot.get("errors") or []
            ready_seq = snapshot.get("ready_seq", 0)
            if not errors and ready_seq > consumed_ready_seq:
                if runtime_status:
                    runtime_status("done", revision, "Browser runtime verification passed: console is clean.", port=port, project_dir=str(project_dir))
                break
            if not errors:
                smoke_ok, smoke_message = _headless_browser_smoke_test(port)
                if smoke_ok:
                    if runtime_status:
                        runtime_status("done", revision, smoke_message, port=port, project_dir=str(project_dir))
                    break
                # A headless browser can catch an early ESM/module-load error before
                # the parent runtime probe receives it. Treat that as a real runtime
                # diagnostic, not as a generic timeout.
                if "runtime error:" in smoke_message.lower() and repair_round < max_repairs:
                    diagnostic = smoke_message.split(": ", 1)[1] if ": " in smoke_message else smoke_message
                    event = {"message": diagnostic, "stack": "", "filename": "", "line": 0, "column": 0, "component": ""}
                    target_path = _runtime_target_path(plan, event)
                    if target_path is None:
                        m = re.search(r'from [\"\']([^\"\']+)[\"\']', diagnostic)
                        if m:
                            imported = m.group(1)
                            candidates = [pp.path for pp in plan if imported in contents.get(pp.path, "") or imported.rstrip("/") in contents.get(pp.path, "")]
                            if len(candidates) == 1:
                                target_path = candidates[0]
                    if target_path is None:
                        problems.append("Headless Chromium detected an early module-load runtime error that could not be mapped to a generated file: " + diagnostic)
                        break
                    target = next(p for p in plan if p.path == target_path)
                    revision += 1
                    emit("error", f"Runtime module error found: {diagnostic}", file=target.path, error=event)
                    if runtime_status:
                        runtime_status("repairing_runtime", revision, f"Browser module error in {target.path}; repairing...", port=port, project_dir=str(project_dir))
                    try:
                        contents[target.path] = _retry_component_with_runtime_error(gateway, plan, target, description, event, contents[target.path])
                        write_components(project_dir, plan, contents)
                        continue
                    except Exception as exc:
                        problems.append(f"{target.path}: browser runtime repair failed: {exc}")
                        break
                problems.append("Browser runtime verification timed out: no clean ready signal was received. " + smoke_message)
                break
            if repair_round >= max_repairs:
                problems.append(f"Browser runtime verification failed after {max_repairs} targeted repairs:\n" + "\n".join(
                    str(e.get("message", e)) for e in errors[:8]
                ))
                break
            event = errors[0]
            target_path = _runtime_target_path(plan, event)
            emit("error", f"Runtime error found: {event.get('message', event)}", file=target_path, error=event)
            if target_path is None:
                problems.append("Browser runtime error could not be mapped to a single generated component:\n" + str(event))
                break
            target = next(p for p in plan if p.path == target_path)
            if runtime_status:
                runtime_status("repairing_runtime", revision, f"Runtime error in {target.path}; repairing only that component...", port=port, project_dir=str(project_dir))
            emit("repair", f"Repairing runtime error in {target.path}", file=target.path, error=event)
            try:
                contents[target.path] = _retry_component_with_runtime_error(
                    gateway, plan, target, description, event, contents[target.path]
                )
            except Exception as exc:
                problems.append(f"{target.path}: runtime repair failed: {exc}")
                break
            (project_dir / "src" / target.path).write_text(contents[target.path], encoding="utf-8")
            revision += 1
            emit("repair", f"Rebuilt {target.path}; retesting application", file=target.path, attempt=revision)
            consumed_ready_seq = max(consumed_ready_seq, ready_seq)
            if runtime_status:
                runtime_status("verifying_runtime", revision, f"Refreshing browser after targeted repair of {target.path}...", port=port, project_dir=str(project_dir))
        else:
            problems.append("Browser runtime verification did not reach a clean state.")

    if problems and process.poll() is None:
        try:
            process.terminate()
        except Exception:
            pass
    return project_dir, port, process, plan, problems
