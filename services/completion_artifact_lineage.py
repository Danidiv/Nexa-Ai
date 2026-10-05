"""Setup 5.57: artifact lineage contract."""
from dataclasses import dataclass, asdict
import hashlib, json

@dataclass(frozen=True)
class ArtifactLineage:
    setup: str
    payload: dict
    digest: str

def _digest(setup, payload):
    raw=json.dumps({"setup":setup,"payload":payload}, sort_keys=True, separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def build_artifact_lineage(payload=None):
    payload=dict(payload or {})
    setup="5.57"
    return ArtifactLineage(setup, payload, _digest(setup,payload))

def valid_artifact_lineage(contract):
    return isinstance(contract, ArtifactLineage) and contract.setup=="5.57" and contract.digest==_digest(contract.setup, contract.payload)
