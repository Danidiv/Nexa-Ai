"""Setup 957: Invoice Tax Abstraction."""
from .phase10_runtime import make_record, validate_record
SETUP="957"
KIND="Invoice Tax Abstraction"
DESCRIPTION="invoice line and tax calculation abstraction"

def build_957(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_957(obj):
    return validate_record(obj, SETUP, KIND)
