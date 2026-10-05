"""Setup 7.91: Requirement-to-Implementation Trace."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.91"
KIND = "Requirement-to-Implementation Trace"
def build_791(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_791(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
