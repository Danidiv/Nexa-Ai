"""Setup 953: Role Permission Compiler."""
from .phase10_runtime import make_record, validate_record
SETUP="953"
KIND="Role Permission Compiler"
DESCRIPTION="role/permission compilation with explicit deny precedence"

def build_953(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_953(obj):
    return validate_record(obj, SETUP, KIND)
