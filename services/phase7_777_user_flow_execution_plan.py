"""Setup 7.77: User Flow Execution Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.77"
KIND = "User Flow Execution Plan"
def build_777(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_777(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
