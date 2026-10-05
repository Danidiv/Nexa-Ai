"""Setup 6.10: Autonomous Debugging Loop."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class AutonomousDebuggingLoop:
    name: str
    stages: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "AutonomousDebuggingLoop":
        data = {"name": self.name, "stages": list(self.stages), "evidence": list(self.evidence)}
        return AutonomousDebuggingLoop(self.name, self.stages, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "stages": list(self.stages), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_autonomous_debugging_loop(name: str, stages: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> AutonomousDebuggingLoop:
    if not name.strip(): raise ValueError("name is required")
    if len(stages) > 128: raise ValueError("stages are bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return AutonomousDebuggingLoop(name.strip(), tuple(str(x) for x in stages), tuple(str(x) for x in evidence)).sealed()

def valid_autonomous_debugging_loop(obj: AutonomousDebuggingLoop) -> bool:
    return obj.valid()
