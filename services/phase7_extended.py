"""Extended Phase 7 deterministic product-builder artifact primitives (7.52-8.00)."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(data: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()).hexdigest()

def _text(v, name):
    if not isinstance(v, str) or not v.strip(): raise ValueError(f"{name} is required")
    return v.strip()

@dataclass(frozen=True)
class BuilderArtifact:
    setup: str
    task_id: str
    kind: str
    payload: tuple[tuple[str, Any], ...]
    digest_value: str = ""
    def sealed(self):
        data={"setup":self.setup,"task_id":self.task_id,"kind":self.kind,"payload":list(self.payload)}
        return BuilderArtifact(self.setup,self.task_id,self.kind,self.payload,_digest(data))
    def valid(self):
        data={"setup":self.setup,"task_id":self.task_id,"kind":self.kind,"payload":list(self.payload)}
        return bool(self.digest_value) and self.digest_value==_digest(data)
    def to_dict(self): return asdict(self)

def build_artifact(setup, task_id, kind, **payload):
    setup=_text(setup,"setup"); task_id=_text(task_id,"task_id"); kind=_text(kind,"kind")
    norm=[]
    for k,v in sorted(payload.items()):
        if isinstance(v,list): v=tuple(v)
        norm.append((k,v))
    return BuilderArtifact(setup,task_id,kind,tuple(norm)).sealed()

def valid_artifact(obj): return isinstance(obj,BuilderArtifact) and obj.valid()
