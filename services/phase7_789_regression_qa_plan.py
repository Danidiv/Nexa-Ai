"""Setup 7.89: Regression QA Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.89"
KIND = "Regression QA Plan"
def build_789(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_789(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
