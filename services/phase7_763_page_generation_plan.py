"""Setup 7.63: Page Generation Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.63"
KIND = "Page Generation Plan"
def build_763(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_763(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
