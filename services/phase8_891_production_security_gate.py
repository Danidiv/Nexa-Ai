"""Setup 8.91: Production Security Gate."""
from .phase8_ext_runtime import artifact,required,bounded,risk,topo,merge,unique
SETUP="8.91"
KIND="Production Security Gate"
DESCRIPTION="aggregate production security checks"
def build_891(task_id, **payload):
    required(task_id,"task_id")
    if "risk" in payload: risk(payload["risk"])
    if "nodes" in payload: topo(payload["nodes"],payload.get("edges",[]))
    if "items" in payload: payload["items"]=unique(bounded(payload["items"]))
    return artifact(SETUP,task_id,KIND,**payload)
def valid_891(obj):
    return getattr(obj,"setup",None)==SETUP and getattr(obj,"kind",None)==KIND and obj.valid()
