"""Setup 9.06: SaaS Workspace Model."""
from .phase8_ext_runtime import artifact,required,bounded,risk,topo,merge,unique
SETUP="9.06"
KIND="SaaS Workspace Model"
DESCRIPTION="workspace membership, invitations and workspace settings"

def build_906(task_id, **payload):
    required(task_id,"task_id")
    if "risk" in payload: risk(payload["risk"])
    if "nodes" in payload:
        topo(payload["nodes"], payload.get("edges", []))
    if "items" in payload: payload["items"]=unique(bounded(payload["items"]))
    if "context" in payload: payload["context"]=merge(payload["context"])
    return artifact(SETUP,task_id,KIND,**payload)

def valid_906(obj):
    return getattr(obj,"setup",None)==SETUP and getattr(obj,"kind",None)==KIND and obj.valid()
