"""Setup 6.95: Regression Analysis."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class RegressionAnalysis:
    task_id: str
    areas: tuple[Any, ...]
    tests: tuple[Any, ...]
    findings: tuple[Any, ...]
    digest: str = ""

    def sealed(self) -> "RegressionAnalysis":
        data={"task_id": self.task_id, "areas": list(self.areas), "tests": list(self.tests), "findings": list(self.findings)}
        d=_digest(data)
        return RegressionAnalysis(self.task_id, self.areas, self.tests, self.findings, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "areas": list(self.areas), "tests": list(self.tests), "findings": list(self.findings)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_regression_analysis(task_id: str, areas: list[str] | tuple[str,...], tests: list[str] | tuple[str,...], findings: list[str] | tuple[str,...]) -> RegressionAnalysis:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(areas), tuple(tests), tuple(findings)]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return RegressionAnalysis(*values, "").sealed()

def valid_regression_analysis(obj: RegressionAnalysis) -> bool:
    return isinstance(obj, RegressionAnalysis) and obj.valid()
