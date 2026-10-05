"""Setup 6.19: Autonomous Engineering Loop."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class AutonomousEngineeringLoop:
    name: str
    phases: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "AutonomousEngineeringLoop":
        data = {"name": self.name, "phases": list(self.phases), "evidence": list(self.evidence)}
        return AutonomousEngineeringLoop(self.name, self.phases, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "phases": list(self.phases), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_autonomous_engineering_loop(name: str, phases: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> AutonomousEngineeringLoop:
    if not name.strip(): raise ValueError("name is required")
    if len(phases) > 128: raise ValueError("phases are bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return AutonomousEngineeringLoop(name.strip(), tuple(str(x) for x in phases), tuple(str(x) for x in evidence)).sealed()

def valid_autonomous_engineering_loop(obj: AutonomousEngineeringLoop) -> bool:
    return obj.valid()
