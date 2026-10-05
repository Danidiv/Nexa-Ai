"""Setup 6.81: Task Intent Extraction."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class TaskIntentExtraction:
    task_id: str
    intent: str
    constraints: tuple[Any, ...]
    signals: tuple[Any, ...]
    digest: str = ""

    def sealed(self) -> "TaskIntentExtraction":
        data={"task_id": self.task_id, "intent": self.intent, "constraints": list(self.constraints), "signals": list(self.signals)}
        d=_digest(data)
        return TaskIntentExtraction(self.task_id, self.intent, self.constraints, self.signals, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "intent": self.intent, "constraints": list(self.constraints), "signals": list(self.signals)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_task_intent_extraction(task_id: str, intent: str, constraints: list[str] | tuple[str,...], signals: list[str] | tuple[str,...]) -> TaskIntentExtraction:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), intent.strip(), tuple(constraints), tuple(signals)]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return TaskIntentExtraction(*values, "").sealed()

def valid_task_intent_extraction(obj: TaskIntentExtraction) -> bool:
    return isinstance(obj, TaskIntentExtraction) and obj.valid()
