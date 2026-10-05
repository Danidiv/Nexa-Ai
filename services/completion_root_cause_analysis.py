"""Setup 6.08: Root Cause Analysis."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class RootCauseAnalysis:
    name: str
    causes: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "RootCauseAnalysis":
        data = {"name": self.name, "causes": list(self.causes), "evidence": list(self.evidence)}
        return RootCauseAnalysis(self.name, self.causes, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "causes": list(self.causes), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_root_cause_analysis(name: str, causes: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> RootCauseAnalysis:
    if not name.strip():
        raise ValueError("name is required")
    if len(causes) > 128:
        raise ValueError("causes are bounded to 128")
    if len(evidence) > 128:
        raise ValueError("evidence is bounded to 128")
    obj = RootCauseAnalysis(name.strip(), tuple(str(x) for x in causes), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_root_cause_analysis(obj: RootCauseAnalysis) -> bool:
    return obj.valid()
