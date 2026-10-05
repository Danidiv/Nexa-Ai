"""Setup 5.76: Deployment Observability."""

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
    metrics: tuple[str, ...]
    events: tuple[str, ...]
    digest: str = ""
    def sealed(self) -> "Contract":
        data = asdict(self); data.pop("digest", None)
        return Contract(self.name, self.metrics, self.events, _digest(data))
    def valid(self) -> bool:
        data = asdict(self); digest = data.pop("digest")
        return bool(digest) and digest == _digest(data)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_contract(name: str, metrics: list[str] | tuple[str, ...] = (), events: list[str] | tuple[str, ...] = ()) -> Contract:
    if not name.strip():
        raise ValueError("name is required")
    if len(metrics) > 64 or len(events) > 128:
        raise ValueError("observability entries are bounded")
    obj = Contract(name.strip(), tuple(str(x) for x in metrics), tuple(str(x) for x in events))
    return obj.sealed()

def valid_contract(obj: Contract) -> bool:
    return obj.valid()
