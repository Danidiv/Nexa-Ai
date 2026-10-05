"""Setup 5.59: release evidence contract."""
from dataclasses import dataclass, asdict
import hashlib, json

@dataclass(frozen=True)
class ReleaseEvidence:
    setup: str
    payload: dict
    digest: str

def _digest(setup, payload):
    raw=json.dumps({"setup":setup,"payload":payload}, sort_keys=True, separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def build_release_evidence(payload=None):
    payload=dict(payload or {})
    setup="5.59"
    return ReleaseEvidence(setup, payload, _digest(setup,payload))

def valid_release_evidence(contract):
    return isinstance(contract, ReleaseEvidence) and contract.setup=="5.59" and contract.digest==_digest(contract.setup, contract.payload)
