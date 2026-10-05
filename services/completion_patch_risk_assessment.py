"""Setup 6.11: Patch Risk Assessment."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class PatchRiskAssessment:
    name: str
    risks: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "PatchRiskAssessment":
        data = {"name": self.name, "risks": list(self.risks), "evidence": list(self.evidence)}
        return PatchRiskAssessment(self.name, self.risks, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "risks": list(self.risks), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_patch_risk_assessment(name: str, risks: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> PatchRiskAssessment:
    if not name.strip(): raise ValueError("name is required")
    if len(risks) > 128: raise ValueError("risks are bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return PatchRiskAssessment(name.strip(), tuple(str(x) for x in risks), tuple(str(x) for x in evidence)).sealed()

def valid_patch_risk_assessment(obj: PatchRiskAssessment) -> bool:
    return obj.valid()
