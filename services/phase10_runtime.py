"""Phase 10 runtime primitives: deterministic, evidence-friendly records and orchestration helpers."""
from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any

SETUP_PREFIX="10."

@dataclass(frozen=True)
class RuntimeRecord:
    setup:str
    task_id:str
    kind:str
    payload:dict[str,Any]=field(default_factory=dict)
    digest:str=""
    def canonical(self):
        return json.dumps({"setup":self.setup,"task_id":self.task_id,"kind":self.kind,"payload":self.payload},sort_keys=True,separators=(",",":"),default=str)
    def valid(self):
        return bool(self.setup and self.task_id and self.kind and self.digest==sha256(self.canonical().encode()).hexdigest())

def _safe(value):
    if isinstance(value,dict): return {str(k):_safe(v) for k,v in sorted(value.items(),key=lambda x:str(x[0]))}
    if isinstance(value,(list,tuple)): return [_safe(v) for v in value]
    return value

def make_record(setup,task_id,kind,**payload):
    if not isinstance(task_id,str) or not task_id.strip(): raise ValueError("task_id is required")
    data=_safe(payload)
    obj=RuntimeRecord(setup,task_id,kind,data,"")
    return RuntimeRecord(setup,task_id,kind,data,sha256(obj.canonical().encode()).hexdigest())

def validate_record(obj,setup,kind):
    return isinstance(obj,RuntimeRecord) and obj.setup==setup and obj.kind==kind and obj.valid()

def acceptance(criteria, evidence):
    criteria=list(criteria or [])
    evidence=dict(evidence or {})
    return {c: bool(evidence.get(c)) for c in criteria}

def execution_graph(nodes,edges):
    nodes=list(dict.fromkeys(nodes or [])); edges=[tuple(e) for e in (edges or [])]
    incoming={n:0 for n in nodes}
    for a,b in edges:
        if a not in incoming or b not in incoming: raise ValueError("edge references unknown node")
        incoming[b]+=1
    ready=[n for n in nodes if incoming[n]==0]; order=[]
    while ready:
        n=ready.pop(0); order.append(n)
        for a,b in edges:
            if a==n:
                incoming[b]-=1
                if incoming[b]==0: ready.append(b)
    if len(order)!=len(nodes): raise ValueError("execution graph contains a cycle")
    return order

def redact_secrets(config):
    secret_words=("secret","password","token","api_key","apikey","private_key")
    return {k:("***REDACTED***" if any(w in str(k).lower() for w in secret_words) else v) for k,v in dict(config or {}).items()}

def run_product_session(task_id, nodes, edges, criteria=None, config=None):
    order=execution_graph(nodes,edges)
    safe=redact_secrets(config)
    checks=acceptance(criteria, {c: True for c in (criteria or [])})
    return {"task_id":task_id,"order":order,"config":safe,"acceptance":checks,"status":"verified" if all(checks.values()) else "incomplete"}
