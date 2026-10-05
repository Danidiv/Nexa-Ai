"""Setup 6.91: Repair Candidate Generation."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class RepairCandidates:
    task_id: str
    candidates: tuple[Any, ...]
    scores: tuple[Any, ...]
    basis: tuple[Any, ...]
    digest: str = ""

    def sealed(self) -> "RepairCandidates":
        data={"task_id": self.task_id, "candidates": list(self.candidates), "scores": list(self.scores), "basis": list(self.basis)}
        d=_digest(data)
        return RepairCandidates(self.task_id, self.candidates, self.scores, self.basis, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "candidates": list(self.candidates), "scores": list(self.scores), "basis": list(self.basis)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_repair_candidates(task_id: str, candidates: list[str] | tuple[str,...], scores: list[str] | tuple[str,...], basis: list[str] | tuple[str,...]) -> RepairCandidates:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(candidates), tuple(scores), tuple(basis)]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return RepairCandidates(*values, "").sealed()

def valid_repair_candidates(obj: RepairCandidates) -> bool:
    return isinstance(obj, RepairCandidates) and obj.valid()
