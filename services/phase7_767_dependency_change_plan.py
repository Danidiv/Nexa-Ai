"""Setup 7.67: Dependency Change Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.67"
KIND = "Dependency Change Plan"
def build_767(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_767(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
