"""Setup 7.94: Browser-Driven Implementation Record."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.94"
KIND = "Browser-Driven Implementation Record"
def build_794(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_794(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
