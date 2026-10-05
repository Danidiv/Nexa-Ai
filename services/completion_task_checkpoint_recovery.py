"""Setup 6.38: Task Checkpoint Recovery."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class TaskCheckpointRecovery:
    task_id: str
    checkpoint: tuple[str, ...]
    recovery: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "TaskCheckpointRecovery":
        data = {'task_id': (self.task_id if not isinstance(self.task_id, tuple) else list(self.task_id)), 'checkpoint': (self.checkpoint if not isinstance(self.checkpoint, tuple) else list(self.checkpoint)), 'recovery': (self.recovery if not isinstance(self.recovery, tuple) else list(self.recovery)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return TaskCheckpointRecovery(self.task_id, self.checkpoint, self.recovery, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'task_id': (self.task_id if not isinstance(self.task_id, tuple) else list(self.task_id)), 'checkpoint': (self.checkpoint if not isinstance(self.checkpoint, tuple) else list(self.checkpoint)), 'recovery': (self.recovery if not isinstance(self.recovery, tuple) else list(self.recovery)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_task_checkpoint_recovery(task_id: str, checkpoint: list[str] | tuple[str, ...], recovery: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> TaskCheckpointRecovery:
    if isinstance(task_id, str) and not task_id.strip(): raise ValueError("task_id is required")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return TaskCheckpointRecovery(task_id.strip(), tuple(str(x) for x in checkpoint), tuple(str(x) for x in recovery), tuple(str(x) for x in evidence)).sealed()

def valid_task_checkpoint_recovery(obj: TaskCheckpointRecovery) -> bool:
    return obj.valid()
