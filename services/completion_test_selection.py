"""Setup 6.88: Test Selection."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class TestSelection:
    task_id: str
    tests: tuple[Any, ...]
    priorities: tuple[Any, ...]
    reasons: tuple[Any, ...]
    digest: str = ""

    def sealed(self) -> "TestSelection":
        data={"task_id": self.task_id, "tests": list(self.tests), "priorities": list(self.priorities), "reasons": list(self.reasons)}
        d=_digest(data)
        return TestSelection(self.task_id, self.tests, self.priorities, self.reasons, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "tests": list(self.tests), "priorities": list(self.priorities), "reasons": list(self.reasons)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_test_selection(task_id: str, tests: list[str] | tuple[str,...], priorities: list[str] | tuple[str,...], reasons: list[str] | tuple[str,...]) -> TestSelection:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(tests), tuple(priorities), tuple(reasons)]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return TestSelection(*values, "").sealed()

def valid_test_selection(obj: TestSelection) -> bool:
    return isinstance(obj, TestSelection) and obj.valid()
