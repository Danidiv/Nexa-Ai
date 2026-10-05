"""Setup 5.92: SLO Contract."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class SLOContract:
    name: str
    objectives: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "SLOContract":
        data = {"name": self.name, "objectives": list(self.objectives), "evidence": list(self.evidence)}
        return SLOContract(self.name, self.objectives, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "objectives": list(self.objectives), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_slo_contract(name: str, objectives: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> SLOContract:
    if not name.strip():
        raise ValueError("name is required")
    if len(objectives) > 32:
        raise ValueError("objectives are bounded to 32")
    if len(evidence) > 64:
        raise ValueError("evidence is bounded to 64")
    obj = SLOContract(name.strip(), tuple(str(x) for x in objectives), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_slo_contract(obj: SLOContract) -> bool:
    return obj.valid()
