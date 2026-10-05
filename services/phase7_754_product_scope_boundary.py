"""Setup 7.54: Product Scope Boundary."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.54"
KIND = "Product Scope Boundary"
def build_754(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_754(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
