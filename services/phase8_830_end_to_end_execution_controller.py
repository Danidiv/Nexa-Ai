"""Setup 8.30: End-to-End Execution Controller."""
from .phase8_runtime import artifact, score_risk, topological, merge_context, bounded, unique_text

SETUP="8.30"
KIND="End-to-End Execution Controller"
DESCRIPTION="coordinate build run test repair verify"

def build_830(task_id, **payload):
    if "risk" in payload: score_risk(payload["risk"])
    if "nodes" in payload: topological(payload["nodes"], payload.get("edges", []))
    if "items" in payload: bounded(payload["items"])
    if "items" in payload: payload["items"]=unique_text(payload["items"])
    return artifact(SETUP, task_id, KIND, **payload)

def valid_830(obj):
    return getattr(obj,"setup",None)==SETUP and getattr(obj,"kind",None)==KIND and obj.valid()
