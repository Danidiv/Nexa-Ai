"""Setup 5.60: release readiness contract."""
from dataclasses import dataclass, asdict
import hashlib, json

@dataclass(frozen=True)
class ReleaseReadiness:
    setup: str
    payload: dict
    digest: str

def _digest(setup, payload):
    raw=json.dumps({"setup":setup,"payload":payload}, sort_keys=True, separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def build_release_readiness(payload=None):
    payload=dict(payload or {})
    setup="5.60"
    return ReleaseReadiness(setup, payload, _digest(setup,payload))

def valid_release_readiness(contract):
    return isinstance(contract, ReleaseReadiness) and contract.setup=="5.60" and contract.digest==_digest(contract.setup, contract.payload)
