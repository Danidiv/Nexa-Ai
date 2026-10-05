"""Setup 7.90: Autonomous Product QA Record."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.90"
KIND = "Autonomous Product QA Record"
def build_790(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_790(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
