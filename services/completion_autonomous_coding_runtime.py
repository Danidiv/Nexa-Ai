"""Setup 6.80: Integrated Autonomous Coding Runtime."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class AutonomousCodingRuntime:
    task_id: str
    phases: tuple[str, ...]
    changed_files: tuple[str, ...]
    tests: tuple[str, ...]
    evidence: tuple[str, ...]
    status: str
    digest: str = ""

    def sealed(self) -> "AutonomousCodingRuntime":
        data={"task_id":self.task_id,"phases":list(self.phases),"changed_files":list(self.changed_files),"tests":list(self.tests),"evidence":list(self.evidence),"status":self.status}
        return AutonomousCodingRuntime(*[self.task_id,self.phases,self.changed_files,self.tests,self.evidence,self.status,_digest(data)])

    def valid(self)->bool:
        data={"task_id":self.task_id,"phases":list(self.phases),"changed_files":list(self.changed_files),"tests":list(self.tests),"evidence":list(self.evidence),"status":self.status}
        return bool(self.digest) and self.digest==_digest(data)

    def to_dict(self)->dict[str,Any]: return asdict(self)

def build_autonomous_coding_runtime(task_id: str, phases: list[str]|tuple[str,...], changed_files: list[str]|tuple[str,...], tests: list[str]|tuple[str,...], evidence: list[str]|tuple[str,...], status: str="running") -> AutonomousCodingRuntime:
    if not isinstance(task_id,str) or not task_id.strip(): raise ValueError("task_id is required")
    if status not in {"running","completed","failed","escalated"}: raise ValueError("invalid status")
    if any(len(x)>128 for x in (phases,changed_files,tests,evidence)): raise ValueError("contract collections are bounded to 128")
    return AutonomousCodingRuntime(task_id.strip(),tuple(str(x) for x in phases),tuple(str(x) for x in changed_files),tuple(str(x) for x in tests),tuple(str(x) for x in evidence),status).sealed()

def valid_autonomous_coding_runtime(obj: AutonomousCodingRuntime)->bool: return obj.valid()
