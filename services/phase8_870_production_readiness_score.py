"""Setup 8.70: Production Readiness Score."""
from .phase8_ext_runtime import artifact,required,bounded,risk,topo,merge,unique
SETUP="8.70"
KIND="Production Readiness Score"
DESCRIPTION="aggregate production readiness signals"
def build_870(task_id, **payload):
    required(task_id,"task_id")
    if "risk" in payload: risk(payload["risk"])
    if "nodes" in payload: topo(payload["nodes"],payload.get("edges",[]))
    if "items" in payload: payload["items"]=unique(bounded(payload["items"]))
    return artifact(SETUP,task_id,KIND,**payload)
def valid_870(obj):
    return getattr(obj,"setup",None)==SETUP and getattr(obj,"kind",None)==KIND and obj.valid()
