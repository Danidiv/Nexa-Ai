"""Setup 7.65: API Generation Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.65"
KIND = "API Generation Plan"
def build_765(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_765(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
