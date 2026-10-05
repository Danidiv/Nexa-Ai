"""Setup 960: SaaS Delivery Foundation."""
from .phase10_runtime import make_record, validate_record
SETUP="960"
KIND="SaaS Delivery Foundation"
DESCRIPTION="integrated customer-to-billing delivery context"

def build_960(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_960(obj):
    return validate_record(obj, SETUP, KIND)
