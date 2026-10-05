"""Setup 7.60: Unified Product Context."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.60"
KIND = "Unified Product Context"
def build_760(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_760(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
