"""Setup 7.93: Full-Stack Generation Session."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.93"
KIND = "Full-Stack Generation Session"
def build_793(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_793(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
