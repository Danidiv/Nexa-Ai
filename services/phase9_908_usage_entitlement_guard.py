"""Setup 9.08: Usage Entitlement Guard."""
from .phase8_ext_runtime import artifact,required,bounded,risk,topo,merge,unique
SETUP="9.08"
KIND="Usage Entitlement Guard"
DESCRIPTION="usage limits, quotas and entitlement checks"

def build_908(task_id, **payload):
    required(task_id,"task_id")
    if "risk" in payload: risk(payload["risk"])
    if "nodes" in payload:
        topo(payload["nodes"], payload.get("edges", []))
    if "items" in payload: payload["items"]=unique(bounded(payload["items"]))
    if "context" in payload: payload["context"]=merge(payload["context"])
    return artifact(SETUP,task_id,KIND,**payload)

def valid_908(obj):
    return getattr(obj,"setup",None)==SETUP and getattr(obj,"kind",None)==KIND and obj.valid()
