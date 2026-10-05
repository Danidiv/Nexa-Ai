"""Setup 7.80: End-to-End Execution Record."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.80"
KIND = "End-to-End Execution Record"
def build_780(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_780(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
