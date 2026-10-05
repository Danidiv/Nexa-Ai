"""Setup 982: Requirement Change Compiler."""
from .phase10_runtime import make_record, validate_record
SETUP="982"
KIND="Requirement Change Compiler"
DESCRIPTION="feedback/requirement deltas into actionable changes"

def build_982(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_982(obj):
    return validate_record(obj, SETUP, KIND)
