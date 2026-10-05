"""Setup 5.96: Backup Restore Readiness."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class BackupRestoreReadiness:
    name: str
    checkpoints: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "BackupRestoreReadiness":
        data = {"name": self.name, "checkpoints": list(self.checkpoints), "evidence": list(self.evidence)}
        return BackupRestoreReadiness(self.name, self.checkpoints, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "checkpoints": list(self.checkpoints), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_backup_restore_readiness(name: str, checkpoints: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> BackupRestoreReadiness:
    if not name.strip():
        raise ValueError("name is required")
    if len(checkpoints) > 32:
        raise ValueError("checkpoints are bounded to 32")
    if len(evidence) > 64:
        raise ValueError("evidence is bounded to 64")
    obj = BackupRestoreReadiness(name.strip(), tuple(str(x) for x in checkpoints), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_backup_restore_readiness(obj: BackupRestoreReadiness) -> bool:
    return obj.valid()
