"""Setup 5.546: Browser Capability Matrix.

maps required capabilities to browser targets.
"""
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any, Dict, List

@dataclass(frozen=True)
class BrowserCapabilityMatrix:
    payload: Dict[str, Any]
    digest: str

def _digest(payload: Dict[str, Any]) -> str:
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True)
    return hashlib.sha256(raw.encode()).hexdigest()

def build_browser_capability_matrix(**kwargs) -> BrowserCapabilityMatrix:
    payload={"setup":"5.546","kind":"Browser Capability Matrix","data":kwargs}
    return BrowserCapabilityMatrix(payload=payload,digest=_digest(payload))

def valid_browser_capability_matrix(item: BrowserCapabilityMatrix) -> bool:
    return bool(item.digest) and item.digest == _digest(item.payload)
