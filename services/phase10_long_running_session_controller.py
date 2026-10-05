"""Setup 993: Long Running Session Controller."""
from .phase10_runtime import make_record, validate_record
SETUP="993"
KIND="Long Running Session Controller"
DESCRIPTION="checkpoint and resume long-running product sessions"

def build_993(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_993(obj):
    return validate_record(obj, SETUP, KIND)
