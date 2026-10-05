"""Setup 6.00: Autonomous Operations Coordinator."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class AutonomousOperationsCoordinator:
    name: str
    tracks: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "AutonomousOperationsCoordinator":
        data = {"name": self.name, "tracks": list(self.tracks), "evidence": list(self.evidence)}
        return AutonomousOperationsCoordinator(self.name, self.tracks, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "tracks": list(self.tracks), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_autonomous_operations_coordinator(name: str, tracks: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> AutonomousOperationsCoordinator:
    if not name.strip():
        raise ValueError("name is required")
    if len(tracks) > 32:
        raise ValueError("tracks are bounded to 32")
    if len(evidence) > 64:
        raise ValueError("evidence is bounded to 64")
    obj = AutonomousOperationsCoordinator(name.strip(), tuple(str(x) for x in tracks), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_autonomous_operations_coordinator(obj: AutonomousOperationsCoordinator) -> bool:
    return obj.valid()
