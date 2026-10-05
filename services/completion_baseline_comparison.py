"""Setup 5.53: baseline comparison contract."""
from dataclasses import dataclass, asdict
import hashlib, json

@dataclass(frozen=True)
class BaselineComparison:
    setup: str
    payload: dict
    digest: str

def _digest(setup, payload):
    raw=json.dumps({"setup":setup,"payload":payload}, sort_keys=True, separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def build_baseline_comparison(payload=None):
    payload=dict(payload or {})
    setup="5.53"
    return BaselineComparison(setup, payload, _digest(setup,payload))

def valid_baseline_comparison(contract):
    return isinstance(contract, BaselineComparison) and contract.setup=="5.53" and contract.digest==_digest(contract.setup, contract.payload)
