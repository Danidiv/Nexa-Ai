"""Setup 996: Release Evidence Synthesizer."""
from .phase10_runtime import make_record, validate_record
SETUP="996"
KIND="Release Evidence Synthesizer"
DESCRIPTION="assemble release evidence from build/test/browser/ops records"

def build_996(task_id, **payload):
    return make_record(SETUP, task_id, KIND, **payload)

def valid_996(obj):
    return validate_record(obj, SETUP, KIND)
