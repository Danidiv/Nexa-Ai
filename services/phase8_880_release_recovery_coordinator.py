"""Setup 8.80: Release Recovery Coordinator."""
from .phase8_ext_runtime import artifact,required,bounded,risk,topo,merge,unique
SETUP="8.80"
KIND="Release Recovery Coordinator"
DESCRIPTION="coordinate release recovery workflows"
def build_880(task_id, **payload):
    required(task_id,"task_id")
    if "risk" in payload: risk(payload["risk"])
    if "nodes" in payload: topo(payload["nodes"],payload.get("edges",[]))
    if "items" in payload: payload["items"]=unique(bounded(payload["items"]))
    return artifact(SETUP,task_id,KIND,**payload)
def valid_880(obj):
    return getattr(obj,"setup",None)==SETUP and getattr(obj,"kind",None)==KIND and obj.valid()
