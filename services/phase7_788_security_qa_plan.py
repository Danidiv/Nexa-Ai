"""Setup 7.88: Security QA Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.88"
KIND = "Security QA Plan"
def build_788(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_788(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
