"""Setup 5.93: Canary Rollout."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class CanaryRollout:
    name: str
    stages: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "CanaryRollout":
        data = {"name": self.name, "stages": list(self.stages), "evidence": list(self.evidence)}
        return CanaryRollout(self.name, self.stages, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "stages": list(self.stages), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_canary_rollout(name: str, stages: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> CanaryRollout:
    if not name.strip():
        raise ValueError("name is required")
    if len(stages) > 32:
        raise ValueError("stages are bounded to 32")
    if len(evidence) > 64:
        raise ValueError("evidence is bounded to 64")
    obj = CanaryRollout(name.strip(), tuple(str(x) for x in stages), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_canary_rollout(obj: CanaryRollout) -> bool:
    return obj.valid()
