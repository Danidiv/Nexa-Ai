"""Setup 5.73: Environment Parity."""

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
    expected: tuple[str, ...]
    actual: tuple[str, ...]
    mismatches: tuple[str, ...]
    digest: str = ""
    def sealed(self) -> "Contract":
        data = asdict(self); data.pop("digest", None)
        return Contract(self.name, self.expected, self.actual, self.mismatches, _digest(data))
    def valid(self) -> bool:
        data = asdict(self); digest = data.pop("digest")
        return bool(digest) and digest == _digest(data)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_contract(name: str, expected: list[str] | tuple[str, ...], actual: list[str] | tuple[str, ...], mismatches: list[str] | tuple[str, ...] = ()) -> Contract:
    if not name.strip():
        raise ValueError("name is required")
    if len(expected) > 64 or len(actual) > 64:
        raise ValueError("environment entries are bounded to 64")
    obj = Contract(name.strip(), tuple(str(x) for x in expected), tuple(str(x) for x in actual), tuple(str(x) for x in mismatches))
    return obj.sealed()

def valid_contract(obj: Contract) -> bool:
    return obj.valid()
