"""Setup 6.97: Completion Evidence Synthesis."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class CompletionEvidence:
    task_id: str
    evidence: tuple[Any, ...]
    claims: tuple[Any, ...]
    status: str
    digest: str = ""

    def sealed(self) -> "CompletionEvidence":
        data={"task_id": self.task_id, "evidence": list(self.evidence), "claims": list(self.claims), "status": self.status}
        d=_digest(data)
        return CompletionEvidence(self.task_id, self.evidence, self.claims, self.status, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "evidence": list(self.evidence), "claims": list(self.claims), "status": self.status}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_completion_evidence(task_id: str, evidence: list[str] | tuple[str,...], claims: list[str] | tuple[str,...], status: str) -> CompletionEvidence:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(evidence), tuple(claims), status.strip()]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return CompletionEvidence(*values, "").sealed()

def valid_completion_evidence(obj: CompletionEvidence) -> bool:
    return isinstance(obj, CompletionEvidence) and obj.valid()
