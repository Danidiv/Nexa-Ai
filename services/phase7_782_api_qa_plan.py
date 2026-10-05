"""Setup 7.82: API QA Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.82"
KIND = "API QA Plan"
def build_782(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_782(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
