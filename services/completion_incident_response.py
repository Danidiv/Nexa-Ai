"""Setup 5.91: Incident Response."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class IncidentResponse:
    name: str
    steps: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "IncidentResponse":
        data = {"name": self.name, "steps": list(self.steps), "evidence": list(self.evidence)}
        return IncidentResponse(self.name, self.steps, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "steps": list(self.steps), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_incident_response(name: str, steps: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> IncidentResponse:
    if not name.strip():
        raise ValueError("name is required")
    if len(steps) > 32:
        raise ValueError("steps are bounded to 32")
    if len(evidence) > 64:
        raise ValueError("evidence is bounded to 64")
    obj = IncidentResponse(name.strip(), tuple(str(x) for x in steps), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_incident_response(obj: IncidentResponse) -> bool:
    return obj.valid()
