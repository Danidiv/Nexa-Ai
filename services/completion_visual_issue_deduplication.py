"""Setup 5.51: visual issue deduplication contract."""
from dataclasses import dataclass, asdict
import hashlib, json

@dataclass(frozen=True)
class VisualIssueDeduplication:
    setup: str
    payload: dict
    digest: str

def _digest(setup, payload):
    raw=json.dumps({"setup":setup,"payload":payload}, sort_keys=True, separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def build_visual_issue_deduplication(payload=None):
    payload=dict(payload or {})
    setup="5.51"
    return VisualIssueDeduplication(setup, payload, _digest(setup,payload))

def valid_visual_issue_deduplication(contract):
    return isinstance(contract, VisualIssueDeduplication) and contract.setup=="5.51" and contract.digest==_digest(contract.setup, contract.payload)
