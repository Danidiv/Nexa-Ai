"""Setup 5.541: Visual Issue Clustering.

clusters visual QA findings by normalized signature.
"""
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any, Dict, List

@dataclass(frozen=True)
class VisualIssueClustering:
    payload: Dict[str, Any]
    digest: str

def _digest(payload: Dict[str, Any]) -> str:
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True)
    return hashlib.sha256(raw.encode()).hexdigest()

def build_visual_issue_clustering(**kwargs) -> VisualIssueClustering:
    payload={"setup":"5.541","kind":"Visual Issue Clustering","data":kwargs}
    return VisualIssueClustering(payload=payload,digest=_digest(payload))

def valid_visual_issue_clustering(item: VisualIssueClustering) -> bool:
    return bool(item.digest) and item.digest == _digest(item.payload)
