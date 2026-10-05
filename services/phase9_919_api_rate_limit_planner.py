"""Setup 9.19: API Rate Limit Planner."""
from .phase8_ext_runtime import artifact,required,bounded,risk,topo,merge,unique
SETUP="9.19"
KIND="API Rate Limit Planner"
DESCRIPTION="tenant/user endpoint quotas and throttling policy"

def build_919(task_id, **payload):
    required(task_id,"task_id")
    if "risk" in payload: risk(payload["risk"])
    if "nodes" in payload:
        topo(payload["nodes"], payload.get("edges", []))
    if "items" in payload: payload["items"]=unique(bounded(payload["items"]))
    if "context" in payload: payload["context"]=merge(payload["context"])
    return artifact(SETUP,task_id,KIND,**payload)

def valid_919(obj):
    return getattr(obj,"setup",None)==SETUP and getattr(obj,"kind",None)==KIND and obj.valid()
