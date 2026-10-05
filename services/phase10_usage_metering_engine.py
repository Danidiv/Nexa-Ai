"""Setup 955: Usage Metering Engine."""
from .phase10_runtime import make_record, validate_record
SETUP="955"
KIND="Usage Metering Engine"
DESCRIPTION="usage counters, limits and period snapshots"

def build_955(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_955(obj):
    return validate_record(obj, SETUP, KIND)
