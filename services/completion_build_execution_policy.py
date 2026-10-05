"""Setup 5.72: Build Execution Policy."""

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
    commands: tuple[str, ...]
    environment_keys: tuple[str, ...]
    digest: str = ""
    def sealed(self) -> "Contract":
        data = asdict(self); data.pop("digest", None)
        return Contract(self.name, self.commands, self.environment_keys, _digest(data))
    def valid(self) -> bool:
        data = asdict(self); digest = data.pop("digest")
        return bool(digest) and digest == _digest(data)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_contract(name: str, commands: list[str] | tuple[str, ...], environment_keys: list[str] | tuple[str, ...] = ()) -> Contract:
    if not name.strip():
        raise ValueError("name is required")
    if len(commands) > 16:
        raise ValueError("commands are bounded to 16")
    if any(not str(x).strip() for x in commands):
        raise ValueError("commands must be non-empty")
    obj = Contract(name.strip(), tuple(str(x) for x in commands), tuple(str(x) for x in environment_keys))
    return obj.sealed()

def valid_contract(obj: Contract) -> bool:
    return obj.valid()
