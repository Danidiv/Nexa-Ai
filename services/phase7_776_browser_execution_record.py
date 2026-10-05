"""Setup 7.76: Browser Execution Record."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.76"
KIND = "Browser Execution Record"
def build_776(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_776(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
