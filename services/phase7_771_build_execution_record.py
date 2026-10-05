"""Setup 7.71: Build Execution Record."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.71"
KIND = "Build Execution Record"
def build_771(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_771(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
