"""Setup 6.98: Outcome Learning."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class OutcomeLearning:
    task_id: str
    patterns: tuple[Any, ...]
    successes: tuple[Any, ...]
    failures: tuple[Any, ...]
    digest: str = ""

    def sealed(self) -> "OutcomeLearning":
        data={"task_id": self.task_id, "patterns": list(self.patterns), "successes": list(self.successes), "failures": list(self.failures)}
        d=_digest(data)
        return OutcomeLearning(self.task_id, self.patterns, self.successes, self.failures, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "patterns": list(self.patterns), "successes": list(self.successes), "failures": list(self.failures)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_outcome_learning(task_id: str, patterns: list[str] | tuple[str,...], successes: list[str] | tuple[str,...], failures: list[str] | tuple[str,...]) -> OutcomeLearning:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(patterns), tuple(successes), tuple(failures)]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return OutcomeLearning(*values, "").sealed()

def valid_outcome_learning(obj: OutcomeLearning) -> bool:
    return isinstance(obj, OutcomeLearning) and obj.valid()
