"""Setup 7.73: Runtime Health Snapshot."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.73"
KIND = "Runtime Health Snapshot"
def build_773(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_773(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
