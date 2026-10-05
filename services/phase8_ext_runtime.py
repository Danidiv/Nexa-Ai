"""Phase 8.51-9.00 additive production-builder runtime primitives."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from typing import Any
import hashlib,json

def canonical(v):
    if isinstance(v,dict): return {str(k):canonical(v[k]) for k in sorted(v)}
    if isinstance(v,(list,tuple)): return [canonical(x) for x in v]
    return v

def digest(v): return hashlib.sha256(json.dumps(canonical(v),sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def required(v,name):
    if not isinstance(v,str) or not v.strip(): raise ValueError(f"{name} is required")
    return v.strip()

def bounded(items,limit=256):
    xs=list(items or [])
    if len(xs)>limit: raise ValueError(f"items exceed {limit}")
    return xs

def risk(v):
    if str(v).lower() not in {"low","medium","high","critical"}: raise ValueError("invalid risk")
    return str(v).lower()

def topo(nodes,edges):
    ns=[]; seen=set()
    for n in nodes or []:
        n=required(n,"node")
        if n not in seen: ns.append(n); seen.add(n)
    deps={n:set() for n in ns}
    for a,b in edges or []:
        if a not in deps or b not in deps: raise ValueError("unknown graph node")
        deps[b].add(a)
    out=[]
    while deps:
        ready=sorted(n for n,d in deps.items() if not d)
        if not ready: raise ValueError("dependency cycle")
        out+=ready
        for n in ready: deps.pop(n)
        for d in deps.values(): d.difference_update(ready)
    return out

def merge(*xs):
    out={}
    for x in xs:
        if not isinstance(x,dict): raise ValueError("context must be object")
        out.update(canonical(x))
    return out

def unique(xs):
    out=[]; seen=set()
    for x in xs or []:
        x=required(x,"item")
        if x not in seen: out.append(x); seen.add(x)
    return out

@dataclass(frozen=True)
class Artifact:
    setup:str; task_id:str; kind:str; payload:dict[str,Any]; digest_value:str=""
    def seal(self):
        d={"setup":self.setup,"task_id":self.task_id,"kind":self.kind,"payload":self.payload}
        return Artifact(self.setup,self.task_id,self.kind,canonical(self.payload),digest(d))
    def valid(self):
        d={"setup":self.setup,"task_id":self.task_id,"kind":self.kind,"payload":self.payload}
        return bool(self.digest_value) and self.digest_value==digest(d)
    def to_dict(self): return asdict(self)

def artifact(setup,task_id,kind,**payload):
    return Artifact(required(setup,"setup"),required(task_id,"task_id"),required(kind,"kind"),canonical(payload)).seal()
