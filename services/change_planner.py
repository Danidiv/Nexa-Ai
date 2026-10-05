"""Setup 4.35: dependency-aware change planning from the static impact graph.

This service turns conservative file-relationship metadata into an ordered,
read-before-write and verify-after-write change plan. It never executes code,
selects tools, edits files, or calls the model.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

MAX_PATHS = 16
VERSION = 1


@dataclass
class ChangePlan:
    """JSON-safe metadata describing likely inspection/change/verification scope."""
    targets: list[str]
    inspect_paths: list[str]
    change_paths: list[str]
    verify_paths: list[str]
    dependency_paths: list[str]
    dependent_paths: list[str]
    rationale: list[str]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["change_plan_version"] = VERSION
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "ChangePlan | None":
        if not isinstance(data, dict) or data.get("change_plan_version") != VERSION:
            return None
        fields = ("targets", "inspect_paths", "change_paths", "verify_paths",
                  "dependency_paths", "dependent_paths", "rationale")
        if any(not isinstance(data.get(field), list) for field in fields):
            return None
        try:
            return cls(
                *[[str(x) for x in data[field] if isinstance(x, str)][:MAX_PATHS] for field in fields]
            )
        except Exception:
            return None

    def summary(self) -> str:
        if not self.targets:
            return "No explicit change targets were identified; inspect the relevant implementation before deciding."
        parts = ["Targets: " + ", ".join(self.targets)]
        if self.dependency_paths:
            parts.append("inspect dependencies: " + ", ".join(self.dependency_paths))
        if self.dependent_paths:
            parts.append("verify dependents: " + ", ".join(self.dependent_paths))
        return "; ".join(parts) + "."


def _unique(values: list[str], limit: int = MAX_PATHS) -> list[str]:
    return list(dict.fromkeys(str(x) for x in values if str(x)))[:limit]


def _match_targets(referenced_paths: dict[str, bool], relationships: dict[str, list[str]], reverse: dict[str, list[str]]) -> list[str]:
    analyzed = list(dict.fromkeys(list(relationships) + list(reverse)))
    targets: list[str] = []
    for raw, exists in list((referenced_paths or {}).items())[:MAX_PATHS]:
        if not exists:
            continue
        normalized = str(raw).replace("\\", "/").lstrip("./")
        exact = next((p for p in analyzed if p == normalized or p.endswith("/" + normalized)), None)
        if exact:
            targets.append(exact)
    return _unique(targets)


def build_change_plan(context: Any) -> ChangePlan:
    """Build a conservative dependency-aware plan from TaskContext metadata."""
    impact = getattr(context, "impact", None)
    if not isinstance(impact, dict):
        return ChangePlan([], [], [], [], [], [], ["No static impact graph is available; observe actual files before editing."])

    relationships = impact.get("relationships") or {}
    reverse = impact.get("reverse_relationships") or {}
    refs = getattr(context, "referenced_paths", {}) or {}
    targets = _match_targets(refs, relationships, reverse)

    dependencies: list[str] = []
    dependents: list[str] = []
    for target in targets:
        dependencies.extend(relationships.get(target, [])[:MAX_PATHS])
        dependents.extend(reverse.get(target, [])[:MAX_PATHS])

    dependencies = _unique([p for p in dependencies if p not in targets])
    dependents = _unique([p for p in dependents if p not in targets and p not in dependencies])

    # Inspection is broader than modification. The graph is a hint, not proof
    # that every related file must change.
    inspect_paths = _unique(dependencies + targets + dependents)
    change_paths = _unique(targets)
    verify_paths = _unique(targets + dependents)

    rationale: list[str] = []
    if targets:
        rationale.append("Referenced existing files are treated as primary change targets.")
    if dependencies:
        rationale.append("Direct dependencies should be read before changing a target.")
    if dependents:
        rationale.append("Direct dependents should be inspected or verified after a target changes.")
    if not targets:
        rationale.append("No existing referenced target was resolved; do not assume a file should be changed.")
    rationale.append("Static relationships are impact hints only; actual file contents and tool results remain authoritative.")

    return ChangePlan(targets, inspect_paths, change_paths, verify_paths, dependencies, dependents, rationale)
