"""Setup 6.14: Data Flow Analysis."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class DataFlowAnalysis:
    name: str
    flows: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "DataFlowAnalysis":
        data = {"name": self.name, "flows": list(self.flows), "evidence": list(self.evidence)}
        return DataFlowAnalysis(self.name, self.flows, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "flows": list(self.flows), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_data_flow_analysis(name: str, flows: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> DataFlowAnalysis:
    if not name.strip(): raise ValueError("name is required")
    if len(flows) > 128: raise ValueError("flows are bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return DataFlowAnalysis(name.strip(), tuple(str(x) for x in flows), tuple(str(x) for x in evidence)).sealed()

def valid_data_flow_analysis(obj: DataFlowAnalysis) -> bool:
    return obj.valid()
