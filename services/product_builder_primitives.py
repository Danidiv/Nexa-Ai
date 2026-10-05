"""Phase 7 shared primitives: additive product-builder foundation."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
import hashlib, json

def digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

def require_text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip(): raise ValueError(f"{name} is required")
    return value.strip()

def bounded(items, name: str, limit: int = 128):
    values=tuple(items or ())
    if len(values)>limit: raise ValueError(f"{name} is bounded to {limit}")
    return values

@dataclass(frozen=True)
class ProductArtifact:
    task_id: str
    kind: str
    payload: tuple[tuple[str, Any], ...]
    digest_value: str = ""
    def sealed(self):
        data={"task_id":self.task_id,"kind":self.kind,"payload":list(self.payload)}
        return ProductArtifact(self.task_id,self.kind,self.payload,digest(data))
    def valid(self):
        data={"task_id":self.task_id,"kind":self.kind,"payload":list(self.payload)}
        return bool(self.digest_value) and self.digest_value==digest(data)
    def to_dict(self): return asdict(self)

def artifact(task_id: str, kind: str, **payload) -> ProductArtifact:
    task_id=require_text(task_id,"task_id"); kind=require_text(kind,"kind")
    normalized=[]
    for k,v in sorted(payload.items()):
        if isinstance(v,list): v=tuple(v)
        normalized.append((k,v))
    return ProductArtifact(task_id,kind,tuple(normalized),"").sealed()
