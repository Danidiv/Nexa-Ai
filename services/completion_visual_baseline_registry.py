"""Setup 5.543: Visual Baseline Registry.

registers versioned visual baselines with digests.
"""
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any, Dict, List

@dataclass(frozen=True)
class VisualBaselineRegistry:
    payload: Dict[str, Any]
    digest: str

def _digest(payload: Dict[str, Any]) -> str:
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True)
    return hashlib.sha256(raw.encode()).hexdigest()

def build_visual_baseline_registry(**kwargs) -> VisualBaselineRegistry:
    payload={"setup":"5.543","kind":"Visual Baseline Registry","data":kwargs}
    return VisualBaselineRegistry(payload=payload,digest=_digest(payload))

def valid_visual_baseline_registry(item: VisualBaselineRegistry) -> bool:
    return bool(item.digest) and item.digest == _digest(item.payload)
