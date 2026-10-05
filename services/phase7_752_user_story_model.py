"""Setup 7.52: User Story Model."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.52"
KIND = "User Story Model"
def build_752(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_752(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
