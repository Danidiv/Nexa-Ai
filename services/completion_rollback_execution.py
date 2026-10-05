"""Setup 5.77: Rollback Execution."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class Contract:
    name: str
    steps: tuple[str, ...]
    safety_gates: tuple[str, ...]
    digest: str = ""
    def sealed(self) -> "Contract":
        data = asdict(self); data.pop("digest", None)
        return Contract(self.name, self.steps, self.safety_gates, _digest(data))
    def valid(self) -> bool:
        data = asdict(self); digest = data.pop("digest")
        return bool(digest) and digest == _digest(data)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_contract(name: str, steps: list[str] | tuple[str, ...], safety_gates: list[str] | tuple[str, ...] = ()) -> Contract:
    if not name.strip():
        raise ValueError("name is required")
    if len(steps) > 32 or len(safety_gates) > 32:
        raise ValueError("rollback entries are bounded to 32")
    obj = Contract(name.strip(), tuple(str(x) for x in steps), tuple(str(x) for x in safety_gates))
    return obj.sealed()

def valid_contract(obj: Contract) -> bool:
    return obj.valid()
