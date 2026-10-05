"""Setup 6.83: Task-to-File Targeting."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class TaskFileTargeting:
    task_id: str
    targets: tuple[Any, ...]
    reasons: tuple[Any, ...]
    digest: str = ""

    def sealed(self) -> "TaskFileTargeting":
        data={"task_id": self.task_id, "targets": list(self.targets), "reasons": list(self.reasons)}
        d=_digest(data)
        return TaskFileTargeting(self.task_id, self.targets, self.reasons, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "targets": list(self.targets), "reasons": list(self.reasons)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_task_file_targeting(task_id: str, targets: list[str] | tuple[str,...], reasons: list[str] | tuple[str,...]) -> TaskFileTargeting:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(targets), tuple(reasons)]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return TaskFileTargeting(*values, "").sealed()

def valid_task_file_targeting(obj: TaskFileTargeting) -> bool:
    return isinstance(obj, TaskFileTargeting) and obj.valid()
