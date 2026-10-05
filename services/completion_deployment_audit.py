"""Setup 5.79: Deployment Audit."""

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
    events: tuple[str, ...]
    sequence: tuple[int, ...]
    digest: str = ""
    def sealed(self) -> "Contract":
        data = asdict(self); data.pop("digest", None)
        return Contract(self.name, self.events, self.sequence, _digest(data))
    def valid(self) -> bool:
        data = asdict(self); digest = data.pop("digest")
        return bool(digest) and digest == _digest(data)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_contract(name: str, events: list[str] | tuple[str, ...], sequence: list[int] | tuple[int, ...]) -> Contract:
    if not name.strip():
        raise ValueError("name is required")
    if len(events) > 256 or len(sequence) > 256:
        raise ValueError("audit entries are bounded to 256")
    if len(events) != len(sequence):
        raise ValueError("events and sequence lengths must match")
    obj = Contract(name.strip(), tuple(str(x) for x in events), tuple(int(x) for x in sequence))
    return obj.sealed()

def valid_contract(obj: Contract) -> bool:
    return obj.valid()
