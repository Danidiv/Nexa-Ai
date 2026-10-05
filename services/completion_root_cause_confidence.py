"""Setup 6.65: Root Cause Confidence."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class RootCauseConfidence:
    task_id: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "RootCauseConfidence":
        data = {"task_id": self.task_id, "inputs": list(self.inputs), "outputs": list(self.outputs), "evidence": list(self.evidence)}
        return RootCauseConfidence(self.task_id, self.inputs, self.outputs, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"task_id": self.task_id, "inputs": list(self.inputs), "outputs": list(self.outputs), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_root_cause_confidence(task_id: str, inputs: list[str] | tuple[str, ...], outputs: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> RootCauseConfidence:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    if len(inputs) > 128 or len(outputs) > 128 or len(evidence) > 128:
        raise ValueError("contract collections are bounded to 128")
    return RootCauseConfidence(task_id.strip(), tuple(str(x) for x in inputs), tuple(str(x) for x in outputs), tuple(str(x) for x in evidence)).sealed()

def valid_root_cause_confidence(obj: RootCauseConfidence) -> bool:
    return obj.valid()
