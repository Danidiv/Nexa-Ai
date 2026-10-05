"""Setup 964: Database Migration Executor."""
from .phase10_runtime import make_record, validate_record
SETUP="964"
KIND="Database Migration Executor"
DESCRIPTION="ordered migration execution records with rollback metadata"

def build_964(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_964(obj):
    return validate_record(obj, SETUP, KIND)
