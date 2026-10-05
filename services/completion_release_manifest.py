"""Setup 5.71: Release Manifest."""

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
    artifacts: tuple[str, ...]
    metadata: tuple[str, ...]
    digest: str = ""
    def sealed(self) -> "Contract":
        data = asdict(self); data.pop("digest", None)
        return Contract(self.name, self.artifacts, self.metadata, _digest(data))
    def valid(self) -> bool:
        data = asdict(self); digest = data.pop("digest")
        return bool(digest) and digest == _digest(data)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_contract(name: str, artifacts: list[str] | tuple[str, ...], metadata: list[str] | tuple[str, ...] = ()) -> Contract:
    if not name.strip():
        raise ValueError("name is required")
    if len(artifacts) > 64:
        raise ValueError("artifacts are bounded to 64")
    if len(metadata) > 32:
        raise ValueError("metadata is bounded to 32")
    obj = Contract(name.strip(), tuple(str(x) for x in artifacts), tuple(str(x) for x in metadata))
    return obj.sealed()

def valid_contract(obj: Contract) -> bool:
    return obj.valid()
