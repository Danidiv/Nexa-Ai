"""Setup 7.74: API Execution Record."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.74"
KIND = "API Execution Record"
def build_774(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_774(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
