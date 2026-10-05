"""Setup 7.83: Database QA Plan."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "7.83"
KIND = "Database QA Plan"
def build_783(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_783(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
