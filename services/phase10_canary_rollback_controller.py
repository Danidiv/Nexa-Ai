"""Setup 976: Canary Rollback Controller."""
from .phase10_runtime import make_record, validate_record
SETUP="976"
KIND="Canary Rollback Controller"
DESCRIPTION="canary evaluation and rollback decisions"

def build_976(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_976(obj):
    return validate_record(obj, SETUP, KIND)
