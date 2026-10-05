"""Setup 7.96: Regression Repair Record."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.96"
KIND = "Regression Repair Record"
def build_796(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_796(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
