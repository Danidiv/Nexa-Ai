"""Setup 4.34: bounded static project relationship and impact analysis.

This service builds a conservative file relationship graph without executing
code. It reads only bounded local source files and extracts local references
(imports, requires, scripts, stylesheets, and template/module references).
It never writes files, runs commands, or calls the model.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import os
import re
from typing import Any

MAX_FILES = 60
MAX_FILE_BYTES = 32_000
MAX_EDGES = 300
MAX_IMPACT = 12

SUPPORTED = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".html", ".htm", ".css"}


@dataclass
class TaskImpact:
    VERSION = 1
    relationships: dict[str, list[str]]
    reverse_relationships: dict[str, list[str]]
    affected_paths: dict[str, list[str]]
    analyzed_files: list[str]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["impact_version"] = self.VERSION
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "TaskImpact | None":
        if not isinstance(data, dict) or data.get("impact_version") != cls.VERSION:
            return None
        try:
            return cls(
                {str(k): [str(x) for x in v if isinstance(x, str)][:MAX_IMPACT]
                 for k, v in (data.get("relationships") or {}).items() if isinstance(k, str) and isinstance(v, list)},
                {str(k): [str(x) for x in v if isinstance(x, str)][:MAX_IMPACT]
                 for k, v in (data.get("reverse_relationships") or {}).items() if isinstance(k, str) and isinstance(v, list)},
                {str(k): [str(x) for x in v if isinstance(x, str)][:MAX_IMPACT]
                 for k, v in (data.get("affected_paths") or {}).items() if isinstance(k, str) and isinstance(v, list)},
                [str(x) for x in data.get("analyzed_files", []) if isinstance(x, str)][:MAX_FILES],
            )
        except Exception:
            return None


def _read_bounded(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeError):
        return ""


def _candidate_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    found: list[Path] = []
    try:
        for current, dirs, files in os.walk(root):
            rel = Path(current).relative_to(root)
            if len(rel.parts) >= 3:
                dirs[:] = []
            dirs[:] = [d for d in sorted(dirs) if d not in {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build"}][:30]
            for name in sorted(files):
                path = Path(current) / name
                if path.suffix.lower() in SUPPORTED:
                    found.append(path)
                    if len(found) >= MAX_FILES:
                        return found
    except OSError:
        return found
    return found


def _refs(content: str, suffix: str) -> list[str]:
    patterns = []
    if suffix in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte"}:
        patterns = [
            r"(?:import\s+(?:[^;]*?\s+from\s+)?|export\s+[^;]*?\s+from\s+|require\s*\(|import\s*\()\s*[\"']([^\"']+)[\"']",
        ]
    elif suffix == ".py":
        patterns = [
            r"^\s*from\s+([.\w]+)\s+import\s+",
            r"^\s*import\s+([.\w]+)",
        ]
    elif suffix in {".html", ".htm"}:
        patterns = [r"(?:src|href)\s*=\s*[\"']([^\"'#]+)[\"']"]
    elif suffix == ".css":
        patterns = [r"@import\s+[\"']([^\"']+)[\"']", r"url\(\s*[\"']?([^\"')]+)"]
    out: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
            value = match.group(1).strip()
            if value and not value.startswith(("http://", "https://", "data:", "#")):
                out.append(value)
    return list(dict.fromkeys(out))[:20]


def _resolve_local(source: Path, raw: str, root: Path) -> Path | None:
    if raw.startswith(("@/", "~", "#")):
        return None
    raw_path = raw.split("?", 1)[0].split("#", 1)[0]
    if not raw_path.startswith((".", "/")) and source.suffix.lower() not in {".py", ".html", ".htm", ".css"}:
        return None
    base = (source.parent / raw_path).resolve()
    candidates = [base]
    if base.suffix == "":
        candidates += [base.with_suffix(ext) for ext in (".js", ".jsx", ".ts", ".tsx", ".py", ".vue", ".svelte", ".html", ".css")]
        candidates += [base / "index.js", base / "index.ts", base / "index.html", base / "__init__.py"]
    try:
        root_resolved = root.resolve()
        for candidate in candidates:
            if candidate.exists() and candidate.is_file() and root_resolved in set(candidate.resolve().parents) | {candidate.resolve()}:
                return candidate.resolve()
    except OSError:
        return None
    return None


def _safe_rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (ValueError, OSError):
        return path.name


def build_task_impact(task: str, workspace_dir: str, projects_dir: str, referenced_paths: dict[str, bool] | None = None) -> TaskImpact:
    """Build a bounded relationship graph and affected-file hints for a task."""
    workspace = Path(workspace_dir)
    projects = Path(projects_dir)
    roots = [workspace]
    # Prefer the project whose name appears in the task; otherwise inspect the workspace.
    match = re.search(r"\bproject\s+(?:named\s+|called\s+)?([A-Za-z0-9_.-]+)", str(task), re.IGNORECASE)
    if match:
        candidate = projects / match.group(1)
        if candidate.is_dir():
            roots = [candidate]
    files: list[tuple[Path, Path]] = []
    for root in roots:
        for path in _candidate_files(root):
            files.append((path, root))
            if len(files) >= MAX_FILES:
                break
        if len(files) >= MAX_FILES:
            break

    relationships: dict[str, list[str]] = {}
    reverse: dict[str, list[str]] = {}
    analyzed: list[str] = []
    edge_count = 0
    for path, root in files:
        rel = _safe_rel(path, root)
        analyzed.append(rel)
        deps: list[str] = []
        content = _read_bounded(path)
        if content:
            for raw in _refs(content, path.suffix.lower()):
                target = _resolve_local(path, raw, root)
                if target is None:
                    continue
                target_rel = _safe_rel(target, root)
                if target_rel != rel and target_rel not in deps:
                    deps.append(target_rel)
                    reverse.setdefault(target_rel, []).append(rel)
                    edge_count += 1
                    if edge_count >= MAX_EDGES:
                        break
        relationships[rel] = deps[:MAX_IMPACT]
        if edge_count >= MAX_EDGES:
            break

    for key in list(reverse):
        reverse[key] = list(dict.fromkeys(reverse[key]))[:MAX_IMPACT]

    refs = list((referenced_paths or {}).keys())[:8]
    affected: dict[str, list[str]] = {}
    for raw in refs:
        normalized = raw.replace("\\", "/").lstrip("./")
        candidates = [normalized]
        if normalized not in relationships:
            candidates.extend([name for name in analyzed if name == normalized or name.endswith("/" + normalized)])
        matched = next((name for name in candidates if name in relationships or name in reverse), None)
        if not matched:
            affected[raw] = []
            continue
        neighbors = []
        neighbors.extend(relationships.get(matched, []))
        neighbors.extend(reverse.get(matched, []))
        affected[raw] = list(dict.fromkeys(neighbors))[:MAX_IMPACT]

    return TaskImpact(relationships, reverse, affected, list(dict.fromkeys(analyzed))[:MAX_FILES])
