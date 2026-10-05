"""Setup 7.72: Development Server Session."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.72"
KIND = "Development Server Session"
def build_772(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_772(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
