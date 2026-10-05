"""Setup 961: Scaffolding Compiler."""
from .phase10_runtime import make_record, validate_record
SETUP="961"
KIND="Scaffolding Compiler"
DESCRIPTION="compile product specification into deterministic file plan"

def build_961(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_961(obj):
    return validate_record(obj, SETUP, KIND)
