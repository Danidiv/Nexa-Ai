"""Setup 5.54: approval policy contract."""
from dataclasses import dataclass, asdict
import hashlib, json

@dataclass(frozen=True)
class ApprovalPolicy:
    setup: str
    payload: dict
    digest: str

def _digest(setup, payload):
    raw=json.dumps({"setup":setup,"payload":payload}, sort_keys=True, separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def build_approval_policy(payload=None):
    payload=dict(payload or {})
    setup="5.54"
    return ApprovalPolicy(setup, payload, _digest(setup,payload))

def valid_approval_policy(contract):
    return isinstance(contract, ApprovalPolicy) and contract.setup=="5.54" and contract.digest==_digest(contract.setup, contract.payload)
