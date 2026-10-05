"""Setup 5.544: Visual Approval Gate.

requires explicit evidence-backed approval for baseline changes.
"""
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any, Dict, List

@dataclass(frozen=True)
class VisualApproval:
    payload: Dict[str, Any]
    digest: str

def _digest(payload: Dict[str, Any]) -> str:
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True)
    return hashlib.sha256(raw.encode()).hexdigest()

def build_visual_approval(**kwargs) -> VisualApproval:
    payload={"setup":"5.544","kind":"Visual Approval Gate","data":kwargs}
    return VisualApproval(payload=payload,digest=_digest(payload))

def valid_visual_approval(item: VisualApproval) -> bool:
    return bool(item.digest) and item.digest == _digest(item.payload)
