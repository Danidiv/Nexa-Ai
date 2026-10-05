"""Setup 6.86: Execution Sequencing."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class ExecutionSequencing:
    task_id: str
    steps: tuple[Any, ...]
    dependencies: tuple[Any, ...]
    barriers: tuple[Any, ...]
    digest: str = ""

    def sealed(self) -> "ExecutionSequencing":
        data={"task_id": self.task_id, "steps": list(self.steps), "dependencies": list(self.dependencies), "barriers": list(self.barriers)}
        d=_digest(data)
        return ExecutionSequencing(self.task_id, self.steps, self.dependencies, self.barriers, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "steps": list(self.steps), "dependencies": list(self.dependencies), "barriers": list(self.barriers)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_execution_sequencing(task_id: str, steps: list[str] | tuple[str,...], dependencies: list[str] | tuple[str,...], barriers: list[str] | tuple[str,...]) -> ExecutionSequencing:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(steps), tuple(dependencies), tuple(barriers)]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return ExecutionSequencing(*values, "").sealed()

def valid_execution_sequencing(obj: ExecutionSequencing) -> bool:
    return isinstance(obj, ExecutionSequencing) and obj.valid()
