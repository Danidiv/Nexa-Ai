"""Setup 5.99: Resource Efficiency."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class ResourceEfficiency:
    name: str
    budgets: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "ResourceEfficiency":
        data = {"name": self.name, "budgets": list(self.budgets), "evidence": list(self.evidence)}
        return ResourceEfficiency(self.name, self.budgets, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "budgets": list(self.budgets), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_resource_efficiency(name: str, budgets: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> ResourceEfficiency:
    if not name.strip():
        raise ValueError("name is required")
    if len(budgets) > 32:
        raise ValueError("budgets are bounded to 32")
    if len(evidence) > 64:
        raise ValueError("evidence is bounded to 64")
    obj = ResourceEfficiency(name.strip(), tuple(str(x) for x in budgets), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_resource_efficiency(obj: ResourceEfficiency) -> bool:
    return obj.valid()
