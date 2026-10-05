"""Setup 5.545: Cross-Browser Matrix.

runs bounded browser compatibility matrix contracts.
"""
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any, Dict, List

@dataclass(frozen=True)
class CrossBrowserMatrix:
    payload: Dict[str, Any]
    digest: str

def _digest(payload: Dict[str, Any]) -> str:
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True)
    return hashlib.sha256(raw.encode()).hexdigest()

def build_cross_browser_matrix(**kwargs) -> CrossBrowserMatrix:
    payload={"setup":"5.545","kind":"Cross-Browser Matrix","data":kwargs}
    return CrossBrowserMatrix(payload=payload,digest=_digest(payload))

def valid_cross_browser_matrix(item: CrossBrowserMatrix) -> bool:
    return bool(item.digest) and item.digest == _digest(item.payload)
