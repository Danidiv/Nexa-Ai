"""Setup 7.55: Architecture Decision Record."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.55"
KIND = "Architecture Decision Record"
def build_755(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_755(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
