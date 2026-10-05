"""Setup 7.84: UI QA Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.84"
KIND = "UI QA Plan"
def build_784(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_784(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
