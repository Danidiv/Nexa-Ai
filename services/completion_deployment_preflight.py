"""Setup 5.74: Deployment Preflight."""

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
    checks: tuple[str, ...]
    blockers: tuple[str, ...]
    digest: str = ""
    def sealed(self) -> "Contract":
        data = asdict(self); data.pop("digest", None)
        return Contract(self.name, self.checks, self.blockers, _digest(data))
    def valid(self) -> bool:
        data = asdict(self); digest = data.pop("digest")
        return bool(digest) and digest == _digest(data)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_contract(name: str, checks: list[str] | tuple[str, ...], blockers: list[str] | tuple[str, ...] = ()) -> Contract:
    if not name.strip():
        raise ValueError("name is required")
    if len(checks) > 32 or len(blockers) > 32:
        raise ValueError("preflight entries are bounded to 32")
    obj = Contract(name.strip(), tuple(str(x) for x in checks), tuple(str(x) for x in blockers))
    return obj.sealed()

def valid_contract(obj: Contract) -> bool:
    return obj.valid()
