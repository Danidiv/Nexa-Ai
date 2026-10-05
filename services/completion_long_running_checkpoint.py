"""Setup 6.18: Long-Running Task Checkpoint."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class LongRunningCheckpoint:
    name: str
    checkpoints: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "LongRunningCheckpoint":
        data = {"name": self.name, "checkpoints": list(self.checkpoints), "evidence": list(self.evidence)}
        return LongRunningCheckpoint(self.name, self.checkpoints, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "checkpoints": list(self.checkpoints), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_long_running_checkpoint(name: str, checkpoints: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> LongRunningCheckpoint:
    if not name.strip(): raise ValueError("name is required")
    if len(checkpoints) > 128: raise ValueError("checkpoints are bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return LongRunningCheckpoint(name.strip(), tuple(str(x) for x in checkpoints), tuple(str(x) for x in evidence)).sealed()

def valid_long_running_checkpoint(obj: LongRunningCheckpoint) -> bool:
    return obj.valid()
