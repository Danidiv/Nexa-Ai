"""Setup 4.38: evidence-based repair and recovery planning.

This module converts incomplete completion evidence into a bounded, deterministic
recovery checklist. It never executes tools, edits files, runs code, or calls
the model. Actual tool results remain authoritative.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

MAX_ITEMS = 24
VERSION = 1


def _norm(value: Any) -> str:
    return str(value or "").replace("\\", "/").lstrip("./")


def _unique(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        item = _norm(value)
        if item and item not in out:
            out.append(item)
    return out[:MAX_ITEMS]


def _verification_path(requirement: str) -> str | None:
    prefix = "verification evidence for "
    if requirement.startswith(prefix):
        return _norm(requirement[len(prefix):])
    return None


@dataclass
class RecoveryItem:
    item_id: str
    kind: str
    target: str
    objective: str
    status: str = "pending"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["recovery_version"] = VERSION
        return data


@dataclass
class EvidenceRecoveryPlan:
    status: str
    items: list[dict[str, Any]]
    missing_evidence: list[str]
    rationale: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "recovery_version": VERSION,
            "status": self.status,
            "items": [dict(x) for x in self.items[:MAX_ITEMS]],
            "missing_evidence": list(self.missing_evidence[:MAX_ITEMS]),
            "rationale": list(self.rationale[:MAX_ITEMS]),
        }

    @classmethod
    def from_dict(cls, data: Any) -> "EvidenceRecoveryPlan | None":
        if not isinstance(data, dict) or data.get("recovery_version") != VERSION:
            return None
        if data.get("status") not in {"not_required", "pending", "complete"}:
            return None
        items: list[dict[str, Any]] = []
        for item in data.get("items", []):
            if not isinstance(item, dict):
                continue
            if not all(k in item for k in ("recovery_version", "item_id", "kind", "target", "objective", "status")):
                continue
            if item.get("status") not in {"pending", "complete"}:
                continue
            items.append({
                "recovery_version": VERSION,
                "item_id": str(item["item_id"]),
                "kind": str(item["kind"]),
                "target": _norm(item["target"]),
                "objective": str(item["objective"]),
                "status": str(item["status"]),
            })
        return cls(
            str(data["status"]),
            items[:MAX_ITEMS],
            [str(x) for x in data.get("missing_evidence", []) if isinstance(x, str)][:MAX_ITEMS],
            [str(x) for x in data.get("rationale", []) if isinstance(x, str)][:MAX_ITEMS],
        )

    def summary(self) -> str:
        if self.status == "not_required":
            return "No evidence recovery is currently required."
        if self.status == "complete":
            return "Evidence recovery is complete."
        pending = [x.get("target", "") for x in self.items if x.get("status") == "pending"]
        if pending:
            return "Recovery pending for: " + ", ".join(pending[:8]) + "."
        return "Evidence recovery is pending."

    def next_item(self) -> dict[str, Any] | None:
        for item in self.items:
            if item.get("status") == "pending":
                return dict(item)
        return None

    def mark_target_complete(self, target: str) -> None:
        target = _norm(target)
        for item in self.items:
            if item.get("status") == "pending" and _norm(item.get("target")) == target:
                item["status"] = "complete"
        self.status = "complete" if self.items and all(x.get("status") == "complete" for x in self.items) else self.status


def build_evidence_recovery(ledger: Any, verification: Any = None, verification_requested: bool = False) -> EvidenceRecoveryPlan:
    """Build a targeted recovery checklist from the current evidence state."""
    if not verification_requested:
        return EvidenceRecoveryPlan("not_required", [], [], ["No post-change verification was requested."])

    missing = list(getattr(ledger, "missing_requirements", []) or [])
    if not missing and getattr(ledger, "status", "insufficient") == "sufficient":
        return EvidenceRecoveryPlan("complete", [], [], ["Completion evidence is already sufficient."])

    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for requirement in missing[:MAX_ITEMS]:
        path = _verification_path(str(requirement))
        if path:
            key = f"verify:{path}"
            if key not in seen:
                seen.add(key)
                items.append(RecoveryItem(
                    item_id=key,
                    kind="verification",
                    target=path,
                    objective=f"Read or otherwise verify {path} and retain successful tool evidence.",
                ).to_dict())
        elif requirement == "complete change-impact verification":
            missing_paths = list(getattr(verification, "missing_paths", []) or [])
            for path in _unique(missing_paths):
                key = f"verify:{path}"
                if key not in seen:
                    seen.add(key)
                    items.append(RecoveryItem(
                        item_id=key,
                        kind="verification",
                        target=path,
                        objective=f"Complete required change-impact verification for {path}.",
                    ).to_dict())
        elif requirement == "successful modification evidence":
            items.append(RecoveryItem(
                item_id="modify:evidence",
                kind="modification",
                target="",
                objective="Repeat or confirm the required modifying action only after inspecting the task state.",
            ).to_dict())

    rationale = [
        "Recovery is derived from missing completion evidence rather than guessed failures.",
        "Verification recovery targets only paths explicitly required by the impact checklist.",
        "Actual tool results remain authoritative; this plan does not execute repairs automatically.",
    ]
    return EvidenceRecoveryPlan("pending" if items else "complete", items[:MAX_ITEMS], missing[:MAX_ITEMS], rationale)
