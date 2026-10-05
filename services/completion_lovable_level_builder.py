"""Setup 7.50: integrated autonomous product builder lifecycle."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
from .product_builder_primitives import digest, require_text, bounded

PHASES=("UNDERSTAND","IMPLEMENT","EXECUTE","VERIFY","REPAIR","RELEASE")

@dataclass(frozen=True)
class LovableLevelBuilder:
    task_id: str
    request: str
    phases: tuple[str,...]
    evidence: tuple[Any,...]
    status: str
    digest_value: str=""
    def sealed(self):
        data={"task_id":self.task_id,"request":self.request,"phases":list(self.phases),"evidence":list(self.evidence),"status":self.status}
        return LovableLevelBuilder(self.task_id,self.request,self.phases,self.evidence,self.status,digest(data))
    def valid(self):
        data={"task_id":self.task_id,"request":self.request,"phases":list(self.phases),"evidence":list(self.evidence),"status":self.status}
        return bool(self.digest_value) and self.digest_value==digest(data)
    def to_dict(self): return asdict(self)

def build_lovable_level_builder(task_id: str, request: str, evidence=(), status="ready") -> LovableLevelBuilder:
    task_id=require_text(task_id,"task_id"); request=require_text(request,"request")
    evidence=bounded(evidence,"evidence")
    if status not in ("ready","running","verified","released","blocked"): raise ValueError("invalid status")
    return LovableLevelBuilder(task_id,request,PHASES,evidence,status,"").sealed()

def valid_lovable_level_builder(obj: LovableLevelBuilder) -> bool:
    return isinstance(obj,LovableLevelBuilder) and obj.phases==PHASES and obj.valid()
