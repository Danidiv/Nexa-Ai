"""Setup 4.36: change-impact verification tracking."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

MAX_PATHS = 24
VERSION = 1


def _norm(value: Any) -> str:
    return str(value or "").replace("\\", "/").lstrip("./")


def _matches(observed: str, required: str) -> bool:
    a, b = _norm(observed), _norm(required)
    return bool(a and b and (a == b or a.endswith("/" + b) or b.endswith("/" + a)))


def _unique(values: list[str]) -> list[str]:
    out = []
    for value in values:
        item = _norm(value)
        if item and item not in out:
            out.append(item)
    return out[:MAX_PATHS]


@dataclass
class ImpactVerification:
    required_paths: list[str]
    completed_paths: list[str]
    missing_paths: list[str]
    status: str
    rationale: list[str]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["verification_version"] = VERSION
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "ImpactVerification | None":
        if not isinstance(data, dict) or data.get("verification_version") != VERSION:
            return None
        fields = ("required_paths", "completed_paths", "missing_paths", "rationale")
        if any(not isinstance(data.get(field), list) for field in fields):
            return None
        if data.get("status") not in {"not_required", "pending", "partial", "complete"}:
            return None
        return cls(
            _unique([x for x in data["required_paths"] if isinstance(x, str)]),
            _unique([x for x in data["completed_paths"] if isinstance(x, str)]),
            _unique([x for x in data["missing_paths"] if isinstance(x, str)]),
            data["status"],
            [str(x) for x in data["rationale"] if isinstance(x, str)][:MAX_PATHS],
        )

    def summary(self) -> str:
        if self.status == "not_required":
            return "No dependency-aware verification is currently required."
        if self.status == "complete":
            return "Change-impact verification complete for all required paths."
        if self.missing_paths:
            return "Verification pending for: " + ", ".join(self.missing_paths) + "."
        return "Verification is pending."


def build_impact_verification(change_plan: Any, modified_resources: Any = None, observed_resources: Any = None) -> ImpactVerification:
    """Calculate which planned paths still need post-change observation."""
    if isinstance(change_plan, dict):
        required = change_plan.get("verify_paths") or []
    else:
        required = getattr(change_plan, "verify_paths", []) or []
    required = _unique([x for x in required if isinstance(x, str)])
    modified = _unique(list(modified_resources or []))
    observed = _unique(list(observed_resources or []))
    if not required:
        required = modified[:MAX_PATHS]
    completed = [path for path in required if any(_matches(item, path) for item in observed)]
    missing = [path for path in required if path not in completed]
    if not required:
        status = "not_required"
    elif not missing:
        status = "complete"
    elif completed:
        status = "partial"
    else:
        status = "pending"
    rationale = []
    if modified:
        rationale.append("Modified resources require post-change verification.")
    if required:
        rationale.append("Dependency-aware verification includes primary targets and direct dependents when the change plan provides them.")
    if missing:
        rationale.append("Unobserved required paths must be checked before claiming completion.")
    rationale.append("Static impact relationships are advisory; actual reads, tests, and tool results remain authoritative.")
    return ImpactVerification(required, completed, missing, status, rationale)
