"""Setup 978: Data Migration Coordinator."""
from .phase10_runtime import make_record, validate_record
SETUP="978"
KIND="Data Migration Coordinator"
DESCRIPTION="data migration batches with checkpoints"

def build_978(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_978(obj):
    return validate_record(obj, SETUP, KIND)
