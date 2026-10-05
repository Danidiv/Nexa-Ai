"""Phase 8 autonomous product-builder runtime primitives. Additive and deterministic."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
import hashlib, json

def _text(v,n):
    if not isinstance(v,str) or not v.strip(): raise ValueError(f"{n} is required")
    return v.strip()

def canonical(v):
    if isinstance(v,dict): return {str(k):canonical(v[k]) for k in sorted(v)}
    if isinstance(v,(list,tuple)): return [canonical(x) for x in v]
    return v

def digest(v):
    return hashlib.sha256(json.dumps(canonical(v),sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

@dataclass(frozen=True)
class Phase8Artifact:
    setup:str; task_id:str; kind:str; payload:dict[str,Any]; digest_value:str=""
    def sealed(self):
        data={"setup":self.setup,"task_id":self.task_id,"kind":self.kind,"payload":self.payload}
        return Phase8Artifact(self.setup,self.task_id,self.kind,canonical(self.payload),digest(data))
    def valid(self):
        data={"setup":self.setup,"task_id":self.task_id,"kind":self.kind,"payload":self.payload}
        return bool(self.digest_value) and self.digest_value==digest(data)
    def to_dict(self): return asdict(self)

def artifact(setup,task_id,kind,**payload):
    return Phase8Artifact(_text(setup,"setup"),_text(task_id,"task_id"),_text(kind,"kind"),canonical(payload)).sealed()

def unique_text(items):
    out=[]; seen=set()
    for x in items or []:
        x=_text(x,"item")
        if x not in seen: out.append(x); seen.add(x)
    return out

def score_risk(risk):
    vals={"low":1,"medium":2,"high":3,"critical":4}
    r=str(risk).lower()
    if r not in vals: raise ValueError("risk must be low, medium, high, or critical")
    return vals[r]

def topological(nodes, edges):
    names=unique_text(nodes); deps={n:set() for n in names}
    for a,b in edges or []:
        if a not in deps or b not in deps: raise ValueError("edge references unknown node")
        deps[b].add(a)
    out=[]
    while deps:
        ready=sorted(n for n,d in deps.items() if not d)
        if not ready: raise ValueError("dependency cycle detected")
        out.extend(ready)
        for n in ready: deps.pop(n)
        for d in deps.values(): d.difference_update(ready)
    return out

def merge_context(*contexts):
    out={}
    for c in contexts:
        if not isinstance(c,dict): raise ValueError("context must be an object")
        out.update(canonical(c))
    return out

def bounded(items,limit=256):
    vals=list(items or [])
    if len(vals)>limit: raise ValueError(f"items exceed {limit}")
    return vals
