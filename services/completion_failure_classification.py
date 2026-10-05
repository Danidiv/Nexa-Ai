"""Setup 6.89: Failure Classification."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class FailureClassification:
    task_id: str
    failures: tuple[Any, ...]
    classes: tuple[Any, ...]
    severity: tuple[Any, ...]
    digest: str = ""

    def sealed(self) -> "FailureClassification":
        data={"task_id": self.task_id, "failures": list(self.failures), "classes": list(self.classes), "severity": list(self.severity)}
        d=_digest(data)
        return FailureClassification(self.task_id, self.failures, self.classes, self.severity, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "failures": list(self.failures), "classes": list(self.classes), "severity": list(self.severity)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_failure_classification(task_id: str, failures: list[str] | tuple[str,...], classes: list[str] | tuple[str,...], severity: list[str] | tuple[str,...]) -> FailureClassification:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(failures), tuple(classes), tuple(severity)]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return FailureClassification(*values, "").sealed()

def valid_failure_classification(obj: FailureClassification) -> bool:
    return isinstance(obj, FailureClassification) and obj.valid()
