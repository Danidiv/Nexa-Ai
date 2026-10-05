"""Setup 970: Autonomous Repair Loop."""
from .phase10_runtime import make_record, validate_record
SETUP="970"
KIND="Autonomous Repair Loop"
DESCRIPTION="repair candidate application and retest records"

def build_970(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_970(obj):
    return validate_record(obj, SETUP, KIND)
