"""Setup 5.56: capability selection contract."""
from dataclasses import dataclass, asdict
import hashlib, json

@dataclass(frozen=True)
class CapabilitySelection:
    setup: str
    payload: dict
    digest: str

def _digest(setup, payload):
    raw=json.dumps({"setup":setup,"payload":payload}, sort_keys=True, separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def build_capability_selection(payload=None):
    payload=dict(payload or {})
    setup="5.56"
    return CapabilitySelection(setup, payload, _digest(setup,payload))

def valid_capability_selection(contract):
    return isinstance(contract, CapabilitySelection) and contract.setup=="5.56" and contract.digest==_digest(contract.setup, contract.payload)
