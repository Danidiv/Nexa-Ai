"""Setup 6.17: Performance Regression Analysis."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class PerformanceRegressionAnalysis:
    name: str
    benchmarks: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "PerformanceRegressionAnalysis":
        data = {"name": self.name, "benchmarks": list(self.benchmarks), "evidence": list(self.evidence)}
        return PerformanceRegressionAnalysis(self.name, self.benchmarks, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "benchmarks": list(self.benchmarks), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_performance_regression_analysis(name: str, benchmarks: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> PerformanceRegressionAnalysis:
    if not name.strip(): raise ValueError("name is required")
    if len(benchmarks) > 128: raise ValueError("benchmarks are bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return PerformanceRegressionAnalysis(name.strip(), tuple(str(x) for x in benchmarks), tuple(str(x) for x in evidence)).sealed()

def valid_performance_regression_analysis(obj: PerformanceRegressionAnalysis) -> bool:
    return obj.valid()
