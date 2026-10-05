"""Setup 7.85: Responsive QA Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.85"
KIND = "Responsive QA Plan"
def build_785(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_785(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
