"""Setup 6.20: Integrated Software Engineering Agent."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class IntegratedSoftwareEngineeringAgent:
    name: str
    capabilities: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "IntegratedSoftwareEngineeringAgent":
        data = {"name": self.name, "capabilities": list(self.capabilities), "evidence": list(self.evidence)}
        return IntegratedSoftwareEngineeringAgent(self.name, self.capabilities, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "capabilities": list(self.capabilities), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_integrated_software_engineering_agent(name: str, capabilities: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> IntegratedSoftwareEngineeringAgent:
    if not name.strip(): raise ValueError("name is required")
    if len(capabilities) > 128: raise ValueError("capabilities are bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return IntegratedSoftwareEngineeringAgent(name.strip(), tuple(str(x) for x in capabilities), tuple(str(x) for x in evidence)).sealed()

def valid_integrated_software_engineering_agent(obj: IntegratedSoftwareEngineeringAgent) -> bool:
    return obj.valid()
