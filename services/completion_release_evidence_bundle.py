"""Setup 5.549: Release Evidence Bundle.

assembles immutable release evidence from QA layers.
"""
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any, Dict, List

@dataclass(frozen=True)
class ReleaseEvidenceBundle:
    payload: Dict[str, Any]
    digest: str

def _digest(payload: Dict[str, Any]) -> str:
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True)
    return hashlib.sha256(raw.encode()).hexdigest()

def build_release_evidence_bundle(**kwargs) -> ReleaseEvidenceBundle:
    payload={"setup":"5.549","kind":"Release Evidence Bundle","data":kwargs}
    return ReleaseEvidenceBundle(payload=payload,digest=_digest(payload))

def valid_release_evidence_bundle(item: ReleaseEvidenceBundle) -> bool:
    return bool(item.digest) and item.digest == _digest(item.payload)
