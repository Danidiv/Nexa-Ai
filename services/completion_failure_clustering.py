"""Setup 6.07: Failure Clustering."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class FailureClustering:
    name: str
    clusters: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "FailureClustering":
        data = {"name": self.name, "clusters": list(self.clusters), "evidence": list(self.evidence)}
        return FailureClustering(self.name, self.clusters, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "clusters": list(self.clusters), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_failure_clustering(name: str, clusters: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> FailureClustering:
    if not name.strip():
        raise ValueError("name is required")
    if len(clusters) > 128:
        raise ValueError("clusters are bounded to 128")
    if len(evidence) > 128:
        raise ValueError("evidence is bounded to 128")
    obj = FailureClustering(name.strip(), tuple(str(x) for x in clusters), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_failure_clustering(obj: FailureClustering) -> bool:
    return obj.valid()
