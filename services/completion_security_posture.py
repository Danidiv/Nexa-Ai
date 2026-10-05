"""Setup 5.98: Security Posture."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class SecurityPosture:
    name: str
    controls: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "SecurityPosture":
        data = {"name": self.name, "controls": list(self.controls), "evidence": list(self.evidence)}
        return SecurityPosture(self.name, self.controls, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "controls": list(self.controls), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_security_posture(name: str, controls: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> SecurityPosture:
    if not name.strip():
        raise ValueError("name is required")
    if len(controls) > 32:
        raise ValueError("controls are bounded to 32")
    if len(evidence) > 64:
        raise ValueError("evidence is bounded to 64")
    obj = SecurityPosture(name.strip(), tuple(str(x) for x in controls), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_security_posture(obj: SecurityPosture) -> bool:
    return obj.valid()
