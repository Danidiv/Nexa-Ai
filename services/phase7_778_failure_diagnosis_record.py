"""Setup 7.78: Failure Diagnosis Record."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.78"
KIND = "Failure Diagnosis Record"
def build_778(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_778(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
