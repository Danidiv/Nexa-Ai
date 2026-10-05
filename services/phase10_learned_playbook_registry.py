"""Setup 990: Learned Playbook Registry."""
from .phase10_runtime import make_record, validate_record
SETUP="990"
KIND="Learned Playbook Registry"
DESCRIPTION="persist reusable engineering/product playbooks"

def build_990(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_990(obj):
    return validate_record(obj, SETUP, KIND)
