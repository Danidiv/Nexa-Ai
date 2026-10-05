"""Setup 7.87: Performance QA Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.87"
KIND = "Performance QA Plan"
def build_787(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_787(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
