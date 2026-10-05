"""Setup 7.98: Completion Evidence Bundle."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.98"
KIND = "Completion Evidence Bundle"
def build_798(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_798(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
