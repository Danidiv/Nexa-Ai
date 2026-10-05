"""Setup 9.03: Authentication Flow Planner."""
from .phase8_ext_runtime import artifact,required,bounded,risk,topo,merge,unique
SETUP="9.03"
KIND="Authentication Flow Planner"
DESCRIPTION="login, signup, password reset and session flows"

def build_903(task_id, **payload):
    required(task_id,"task_id")
    if "risk" in payload: risk(payload["risk"])
    if "nodes" in payload:
        topo(payload["nodes"], payload.get("edges", []))
    if "items" in payload: payload["items"]=unique(bounded(payload["items"]))
    if "context" in payload: payload["context"]=merge(payload["context"])
    return artifact(SETUP,task_id,KIND,**payload)

def valid_903(obj):
    return getattr(obj,"setup",None)==SETUP and getattr(obj,"kind",None)==KIND and obj.valid()
