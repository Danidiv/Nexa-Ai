"""Setup 956: Billing Reconciliation Engine."""
from .phase10_runtime import make_record, validate_record
SETUP="956"
KIND="Billing Reconciliation Engine"
DESCRIPTION="invoice/payment reconciliation with mismatch reporting"

def build_956(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_956(obj):
    return validate_record(obj, SETUP, KIND)
