"""Setup 7.53: Acceptance Criteria Matrix."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.53"
KIND = "Acceptance Criteria Matrix"
def build_753(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_753(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
