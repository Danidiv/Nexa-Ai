"""Setup 6.12: Change Validation."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class ChangeValidation:
    name: str
    checks: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "ChangeValidation":
        data = {"name": self.name, "checks": list(self.checks), "evidence": list(self.evidence)}
        return ChangeValidation(self.name, self.checks, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "checks": list(self.checks), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_change_validation(name: str, checks: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> ChangeValidation:
    if not name.strip(): raise ValueError("name is required")
    if len(checks) > 128: raise ValueError("checks are bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return ChangeValidation(name.strip(), tuple(str(x) for x in checks), tuple(str(x) for x in evidence)).sealed()

def valid_change_validation(obj: ChangeValidation) -> bool:
    return obj.valid()
