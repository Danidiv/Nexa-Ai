"""Setup 8.27: User Flow Execution Coordinator."""
from .phase8_runtime import artifact, score_risk, topological, merge_context, bounded, unique_text

SETUP="8.27"
KIND="User Flow Execution Coordinator"
DESCRIPTION="compile user flow steps and dependencies"

def build_827(task_id, **payload):
    if "risk" in payload: score_risk(payload["risk"])
    if "nodes" in payload: topological(payload["nodes"], payload.get("edges", []))
    if "items" in payload: bounded(payload["items"])
    if "items" in payload: payload["items"]=unique_text(payload["items"])
    return artifact(SETUP, task_id, KIND, **payload)

def valid_827(obj):
    return getattr(obj,"setup",None)==SETUP and getattr(obj,"kind",None)==KIND and obj.valid()
