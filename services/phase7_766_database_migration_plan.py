"""Setup 7.66: Database Migration Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.66"
KIND = "Database Migration Plan"
def build_766(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_766(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
