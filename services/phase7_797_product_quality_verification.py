"""Setup 7.97: Product Quality Verification."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.97"
KIND = "Product Quality Verification"
def build_797(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_797(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
