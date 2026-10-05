"""Setup 5.78: Release Promotion."""

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
    candidate: str
    evidence: tuple[str, ...]
    approved: bool
    digest: str = ""
    def sealed(self) -> "Contract":
        data = asdict(self); data.pop("digest", None)
        return Contract(self.name, self.candidate, self.evidence, self.approved, _digest(data))
    def valid(self) -> bool:
        data = asdict(self); digest = data.pop("digest")
        return bool(digest) and digest == _digest(data)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_contract(name: str, candidate: str, evidence: list[str] | tuple[str, ...] = (), approved: bool = False) -> Contract:
    if not name.strip():
        raise ValueError("name is required")
    if not candidate.strip():
        raise ValueError("candidate is required")
    if len(evidence) > 64:
        raise ValueError("evidence is bounded to 64")
    obj = Contract(name.strip(), candidate.strip(), tuple(str(x) for x in evidence), bool(approved))
    return obj.sealed()

def valid_contract(obj: Contract) -> bool:
    return obj.valid()
