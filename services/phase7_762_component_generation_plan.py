"""Setup 7.62: Component Generation Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.62"
KIND = "Component Generation Plan"
def build_762(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_762(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
