"""Setup 7.86: Accessibility QA Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.86"
KIND = "Accessibility QA Plan"
def build_786(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_786(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
