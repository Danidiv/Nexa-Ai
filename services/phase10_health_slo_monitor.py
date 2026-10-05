"""Setup 973: Health SLO Monitor."""
from .phase10_runtime import make_record, validate_record
SETUP="973"
KIND="Health SLO Monitor"
DESCRIPTION="health and SLO evaluation"

def build_973(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_973(obj):
    return validate_record(obj, SETUP, KIND)
