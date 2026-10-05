"""Setup 5.58: repair execution contract."""
from dataclasses import dataclass, asdict
import hashlib, json

@dataclass(frozen=True)
class RepairExecution:
    setup: str
    payload: dict
    digest: str

def _digest(setup, payload):
    raw=json.dumps({"setup":setup,"payload":payload}, sort_keys=True, separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def build_repair_execution(payload=None):
    payload=dict(payload or {})
    setup="5.58"
    return RepairExecution(setup, payload, _digest(setup,payload))

def valid_repair_execution(contract):
    return isinstance(contract, RepairExecution) and contract.setup=="5.58" and contract.digest==_digest(contract.setup, contract.payload)
