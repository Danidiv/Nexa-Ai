"""Setup 7.64: Backend Service Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.64"
KIND = "Backend Service Plan"
def build_764(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_764(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
