"""Setup 6.76: Autonomous Stop Conditions."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class AutonomousStopConditions:
    task_id: str
    items: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self)->"AutonomousStopConditions":
        data={"task_id":self.task_id,"items":list(self.items),"evidence":list(self.evidence)}
        return AutonomousStopConditions(self.task_id,self.items,self.evidence,_digest(data))

    def valid(self)->bool:
        data={"task_id":self.task_id,"items":list(self.items),"evidence":list(self.evidence)}
        return bool(self.digest) and self.digest==_digest(data)

    def to_dict(self)->dict[str,Any]: return asdict(self)

def build_autonomous_stop_conditions(task_id: str, items: list[str]|tuple[str,...], evidence: list[str]|tuple[str,...]) -> AutonomousStopConditions:
    if not isinstance(task_id,str) or not task_id.strip(): raise ValueError("task_id is required")
    if len(items)>128 or len(evidence)>128: raise ValueError("contract collections are bounded to 128")
    return AutonomousStopConditions(task_id.strip(),tuple(str(x) for x in items),tuple(str(x) for x in evidence)).sealed()

def valid_autonomous_stop_conditions(obj: AutonomousStopConditions)->bool: return obj.valid()
