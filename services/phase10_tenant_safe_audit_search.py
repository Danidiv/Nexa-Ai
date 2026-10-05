"""Setup 959: Tenant Safe Audit Search."""
from .phase10_runtime import make_record, validate_record
SETUP="959"
KIND="Tenant Safe Audit Search"
DESCRIPTION="tenant-scoped audit indexing and search"

def build_959(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_959(obj):
    return validate_record(obj, SETUP, KIND)
