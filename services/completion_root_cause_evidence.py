"""Setup 6.90: Root Cause Evidence."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class RootCauseEvidence:
    task_id: str
    causes: tuple[Any, ...]
    evidence: tuple[Any, ...]
    confidence: tuple[Any, ...]
    digest: str = ""

    def sealed(self) -> "RootCauseEvidence":
        data={"task_id": self.task_id, "causes": list(self.causes), "evidence": list(self.evidence), "confidence": list(self.confidence)}
        d=_digest(data)
        return RootCauseEvidence(self.task_id, self.causes, self.evidence, self.confidence, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "causes": list(self.causes), "evidence": list(self.evidence), "confidence": list(self.confidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_root_cause_evidence(task_id: str, causes: list[str] | tuple[str,...], evidence: list[str] | tuple[str,...], confidence: list[str] | tuple[str,...]) -> RootCauseEvidence:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(causes), tuple(evidence), tuple(confidence)]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return RootCauseEvidence(*values, "").sealed()

def valid_root_cause_evidence(obj: RootCauseEvidence) -> bool:
    return isinstance(obj, RootCauseEvidence) and obj.valid()
