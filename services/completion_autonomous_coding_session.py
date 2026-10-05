"""Setup 6.39: Autonomous Coding Session."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class AutonomousCodingSession:
    task_id: str
    steps: tuple[str, ...]
    state: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "AutonomousCodingSession":
        data = {'task_id': (self.task_id if not isinstance(self.task_id, tuple) else list(self.task_id)), 'steps': (self.steps if not isinstance(self.steps, tuple) else list(self.steps)), 'state': (self.state if not isinstance(self.state, tuple) else list(self.state)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return AutonomousCodingSession(self.task_id, self.steps, self.state, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'task_id': (self.task_id if not isinstance(self.task_id, tuple) else list(self.task_id)), 'steps': (self.steps if not isinstance(self.steps, tuple) else list(self.steps)), 'state': (self.state if not isinstance(self.state, tuple) else list(self.state)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_autonomous_coding_session(task_id: str, steps: list[str] | tuple[str, ...], state: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> AutonomousCodingSession:
    if isinstance(task_id, str) and not task_id.strip(): raise ValueError("task_id is required")
    if len(steps) > 128: raise ValueError("steps is bounded to 128")
    if len(state) > 128: raise ValueError("state is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return AutonomousCodingSession(task_id.strip(), tuple(str(x) for x in steps), tuple(str(x) for x in state), tuple(str(x) for x in evidence)).sealed()

def valid_autonomous_coding_session(obj: AutonomousCodingSession) -> bool:
    return obj.valid()
