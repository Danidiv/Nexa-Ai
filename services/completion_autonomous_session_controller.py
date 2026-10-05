"""Setup 6.99: Autonomous Session Controller."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class AutonomousSessionController:
    task_id: str
    phases: tuple[Any, ...]
    current: str
    status: str
    digest: str = ""

    def sealed(self) -> "AutonomousSessionController":
        data={"task_id": self.task_id, "phases": list(self.phases), "current": self.current, "status": self.status}
        d=_digest(data)
        return AutonomousSessionController(self.task_id, self.phases, self.current, self.status, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "phases": list(self.phases), "current": self.current, "status": self.status}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_autonomous_session_controller(task_id: str, phases: list[str] | tuple[str,...], current: str, status: str) -> AutonomousSessionController:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(phases), current.strip(), status.strip()]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return AutonomousSessionController(*values, "").sealed()

def valid_autonomous_session_controller(obj: AutonomousSessionController) -> bool:
    return isinstance(obj, AutonomousSessionController) and obj.valid()
