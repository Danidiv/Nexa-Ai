"""Setup 958: Support Admin Action Guard."""
from .phase10_runtime import make_record, validate_record
SETUP="958"
KIND="Support Admin Action Guard"
DESCRIPTION="audited support/admin actions with authorization checks"

def build_958(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_958(obj):
    return validate_record(obj, SETUP, KIND)
