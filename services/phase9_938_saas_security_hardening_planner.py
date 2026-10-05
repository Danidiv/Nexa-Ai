"""Setup 9.38: SaaS Security Hardening Planner."""
from .phase8_ext_runtime import artifact,required,bounded,risk,topo,merge,unique
SETUP="9.38"
KIND="SaaS Security Hardening Planner"
DESCRIPTION="tenant isolation, auth, API and data security controls"

def build_938(task_id, **payload):
    required(task_id,"task_id")
    if "risk" in payload: risk(payload["risk"])
    if "nodes" in payload:
        topo(payload["nodes"], payload.get("edges", []))
    if "items" in payload: payload["items"]=unique(bounded(payload["items"]))
    if "context" in payload: payload["context"]=merge(payload["context"])
    return artifact(SETUP,task_id,KIND,**payload)

def valid_938(obj):
    return getattr(obj,"setup",None)==SETUP and getattr(obj,"kind",None)==KIND and obj.valid()
