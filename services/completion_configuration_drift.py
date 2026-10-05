"""Setup 5.95: Configuration Drift."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class ConfigurationDrift:
    name: str
    changes: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "ConfigurationDrift":
        data = {"name": self.name, "changes": list(self.changes), "evidence": list(self.evidence)}
        return ConfigurationDrift(self.name, self.changes, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "changes": list(self.changes), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_configuration_drift(name: str, changes: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> ConfigurationDrift:
    if not name.strip():
        raise ValueError("name is required")
    if len(changes) > 32:
        raise ValueError("changes are bounded to 32")
    if len(evidence) > 64:
        raise ValueError("evidence is bounded to 64")
    obj = ConfigurationDrift(name.strip(), tuple(str(x) for x in changes), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_configuration_drift(obj: ConfigurationDrift) -> bool:
    return obj.valid()
