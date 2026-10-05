"""Setup 6.16: Dependency Risk Analysis."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class DependencyRiskAnalysis:
    name: str
    dependencies: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "DependencyRiskAnalysis":
        data = {"name": self.name, "dependencies": list(self.dependencies), "evidence": list(self.evidence)}
        return DependencyRiskAnalysis(self.name, self.dependencies, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "dependencies": list(self.dependencies), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_dependency_risk_analysis(name: str, dependencies: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> DependencyRiskAnalysis:
    if not name.strip(): raise ValueError("name is required")
    if len(dependencies) > 128: raise ValueError("dependencies are bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return DependencyRiskAnalysis(name.strip(), tuple(str(x) for x in dependencies), tuple(str(x) for x in evidence)).sealed()

def valid_dependency_risk_analysis(obj: DependencyRiskAnalysis) -> bool:
    return obj.valid()
