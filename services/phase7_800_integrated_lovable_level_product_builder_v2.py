"""Setup 8.00: Integrated Lovable-Level Product Builder V2."""
from .phase7_extended import build_artifact, valid_artifact
SETUP = "8.00"
KIND = "Integrated Lovable-Level Product Builder V2"
def build_800(task_id: str, **payload):
    return build_artifact(SETUP, task_id, KIND, **payload)
def valid_800(obj):
    return valid_artifact(obj) and obj.setup == SETUP and obj.kind == KIND
