"""Setup 5.80: Release Deployment Agent."""

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
    stages: tuple[str, ...]
    evidence: tuple[str, ...]
    ready: bool
    digest: str = ""
    def sealed(self) -> "Contract":
        data = asdict(self); data.pop("digest", None)
        return Contract(self.name, self.stages, self.evidence, self.ready, _digest(data))
    def valid(self) -> bool:
        data = asdict(self); digest = data.pop("digest")
        return bool(digest) and digest == _digest(data)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_contract(name: str, stages: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = (), ready: bool = False) -> Contract:
    if not name.strip():
        raise ValueError("name is required")
    if len(stages) > 32 or len(evidence) > 128:
        raise ValueError("workflow entries are bounded")
    obj = Contract(name.strip(), tuple(str(x) for x in stages), tuple(str(x) for x in evidence), bool(ready))
    return obj.sealed()

def valid_contract(obj: Contract) -> bool:
    return obj.valid()
