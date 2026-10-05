"""Setup 7.81: Functional QA Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.81"
KIND = "Functional QA Plan"
def build_781(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_781(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
