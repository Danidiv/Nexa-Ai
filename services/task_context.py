"""Setup 4.33: safe local context discovery for planning.

The context index is deliberately metadata-only: it discovers existing project,
workspace, directory, and file names without reading file contents or executing
commands. This lets planning become context-aware without bypassing the agent's
normal observe/read/validate/execute lifecycle.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import os
import re
from typing import Any


@dataclass
class TaskContext:
    workspace_exists: bool
    project_names: list[str]
    workspace_paths: list[str]
    project_paths: dict[str, list[str]]
    referenced_paths: dict[str, bool]
    impact: Any | None = None
    change_plan: Any | None = None
    codebase_intelligence: Any | None = None

    VERSION = 1

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["context_version"] = self.VERSION
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "TaskContext | None":
        if not isinstance(data, dict) or data.get("context_version") != cls.VERSION:
            return None
        try:
            return cls(
                bool(data.get("workspace_exists", False)),
                [str(x) for x in data.get("project_names", []) if isinstance(x, str)],
                [str(x) for x in data.get("workspace_paths", []) if isinstance(x, str)],
                {
                    str(k): [str(x) for x in v if isinstance(x, str)]
                    for k, v in (data.get("project_paths") or {}).items()
                    if isinstance(k, str) and isinstance(v, list)
                },
                {str(k): bool(v) for k, v in (data.get("referenced_paths") or {}).items() if isinstance(k, str)},
                data.get("impact"),
                data.get("change_plan"),
                data.get("codebase_intelligence"),
            )
        except Exception:
            return None


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def _shallow_paths(root: Path, max_items: int = 80) -> list[str]:
    if not root.is_dir():
        return []
    found: list[str] = []
    try:
        for current, dirs, files in os.walk(root):
            current_path = Path(current)
            rel_depth = len(current_path.relative_to(root).parts)
            if rel_depth >= 2:
                dirs[:] = []
            dirs[:] = sorted(dirs)[:40]
            for name in sorted(files)[:80]:
                found.append(_safe_relative(current_path / name, root))
                if len(found) >= max_items:
                    return found
    except OSError:
        return found
    return found


def _extract_paths(task: str) -> list[str]:
    matches = re.findall(
        r"(?<!\w)(?:[A-Za-z]:[\\/])?[^\s,;:'\"]+\.(?:html?|css|js|jsx|ts|tsx|py|json|md|txt|yml|yaml|sql|java|cpp|c|h|vue|svelte)(?!\w)",
        task,
        re.IGNORECASE,
    )
    return list(dict.fromkeys(matches))[:8]


def build_task_context(task: str, workspace_dir: str, projects_dir: str) -> TaskContext:
    workspace = Path(workspace_dir)
    projects = Path(projects_dir)
    project_names: list[str] = []
    project_paths: dict[str, list[str]] = {}

    try:
        if projects.is_dir():
            project_names = sorted(p.name for p in projects.iterdir() if p.is_dir())[:50]
            for name in project_names:
                project_paths[name] = _shallow_paths(projects / name)
    except OSError:
        pass

    workspace_paths = _shallow_paths(workspace)
    refs = {}
    project_match = re.search(r"\bproject\s+(?:named\s+|called\s+)?([A-Za-z0-9_.-]+)", str(task), re.IGNORECASE)
    selected_project = projects / project_match.group(1) if project_match and (projects / project_match.group(1)).is_dir() else None
    for raw in _extract_paths(task):
        candidate = Path(raw)
        candidates = [workspace / raw, projects / raw]
        if selected_project is not None:
            candidates.insert(0, selected_project / raw)
        if candidate.is_absolute():
            candidates.insert(0, candidate)
        refs[raw] = any(p.exists() for p in candidates)

    context = TaskContext(
        workspace_exists=workspace.is_dir(),
        project_names=project_names,
        workspace_paths=workspace_paths,
        project_paths=project_paths,
        referenced_paths=refs,
    )
    # Setup 4.34: bounded static relationship analysis. It is deliberately
    # separate from metadata discovery and never executes project code.
    try:
        from services.task_impact import build_task_impact
        impact = build_task_impact(task, workspace_dir, projects_dir, refs)
        context.impact = impact.to_dict()
        from services.change_planner import build_change_plan
        context.change_plan = build_change_plan(context).to_dict()
        from services.completion_codebase_intelligence import intelligence_report
        selected_root = selected_project if selected_project is not None else workspace
        context.codebase_intelligence = intelligence_report(str(selected_root), task)
    except Exception:
        context.impact = None
    return context
