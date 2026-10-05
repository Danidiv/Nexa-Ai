"""Setup 6.06: Test Execution Matrix."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class TestExecutionMatrix:
    name: str
    runs: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "TestExecutionMatrix":
        data = {"name": self.name, "runs": list(self.runs), "evidence": list(self.evidence)}
        return TestExecutionMatrix(self.name, self.runs, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "runs": list(self.runs), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_test_execution_matrix(name: str, runs: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> TestExecutionMatrix:
    if not name.strip():
        raise ValueError("name is required")
    if len(runs) > 128:
        raise ValueError("runs are bounded to 128")
    if len(evidence) > 128:
        raise ValueError("evidence is bounded to 128")
    obj = TestExecutionMatrix(name.strip(), tuple(str(x) for x in runs), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_test_execution_matrix(obj: TestExecutionMatrix) -> bool:
    return obj.valid()
