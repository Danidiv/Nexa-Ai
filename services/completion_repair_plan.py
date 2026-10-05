"""Setup 6.09: Repair Plan."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class RepairPlan:
    name: str
    repairs: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "RepairPlan":
        data = {"name": self.name, "repairs": list(self.repairs), "evidence": list(self.evidence)}
        return RepairPlan(self.name, self.repairs, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "repairs": list(self.repairs), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_repair_plan(name: str, repairs: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> RepairPlan:
    if not name.strip():
        raise ValueError("name is required")
    if len(repairs) > 128:
        raise ValueError("repairs are bounded to 128")
    if len(evidence) > 128:
        raise ValueError("evidence is bounded to 128")
    obj = RepairPlan(name.strip(), tuple(str(x) for x in repairs), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_repair_plan(obj: RepairPlan) -> bool:
    return obj.valid()
