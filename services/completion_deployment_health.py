"""Setup 5.75: Deployment Health."""

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
    endpoints: tuple[str, ...]
    checks: tuple[str, ...]
    healthy: bool
    digest: str = ""
    def sealed(self) -> "Contract":
        data = asdict(self); data.pop("digest", None)
        return Contract(self.name, self.endpoints, self.checks, self.healthy, _digest(data))
    def valid(self) -> bool:
        data = asdict(self); digest = data.pop("digest")
        return bool(digest) and digest == _digest(data)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_contract(name: str, endpoints: list[str] | tuple[str, ...], checks: list[str] | tuple[str, ...], healthy: bool) -> Contract:
    if not name.strip():
        raise ValueError("name is required")
    if len(endpoints) > 32 or len(checks) > 64:
        raise ValueError("health entries are bounded")
    obj = Contract(name.strip(), tuple(str(x) for x in endpoints), tuple(str(x) for x in checks), bool(healthy))
    return obj.sealed()

def valid_contract(obj: Contract) -> bool:
    return obj.valid()
