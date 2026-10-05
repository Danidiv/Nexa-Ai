"""Setup 5.94: Feature Flag Safety."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class FeatureFlagSafety:
    name: str
    flags: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "FeatureFlagSafety":
        data = {"name": self.name, "flags": list(self.flags), "evidence": list(self.evidence)}
        return FeatureFlagSafety(self.name, self.flags, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "flags": list(self.flags), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_feature_flag_safety(name: str, flags: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> FeatureFlagSafety:
    if not name.strip():
        raise ValueError("name is required")
    if len(flags) > 32:
        raise ValueError("flags are bounded to 32")
    if len(evidence) > 64:
        raise ValueError("evidence is bounded to 64")
    obj = FeatureFlagSafety(name.strip(), tuple(str(x) for x in flags), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_feature_flag_safety(obj: FeatureFlagSafety) -> bool:
    return obj.valid()
