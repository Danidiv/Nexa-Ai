"""Setup 962: Package Dependency Executor."""
from .phase10_runtime import make_record, validate_record
SETUP="962"
KIND="Package Dependency Executor"
DESCRIPTION="dependency change planning and command records"

def build_962(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_962(obj):
    return validate_record(obj, SETUP, KIND)
