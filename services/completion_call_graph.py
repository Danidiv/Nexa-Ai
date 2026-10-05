"""Setup 6.03: Call Graph."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class CallGraph:
    name: str
    edges: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "CallGraph":
        data = {"name": self.name, "edges": list(self.edges), "evidence": list(self.evidence)}
        return CallGraph(self.name, self.edges, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "edges": list(self.edges), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_call_graph(name: str, edges: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> CallGraph:
    if not name.strip():
        raise ValueError("name is required")
    if len(edges) > 128:
        raise ValueError("edges are bounded to 128")
    if len(evidence) > 128:
        raise ValueError("evidence is bounded to 128")
    obj = CallGraph(name.strip(), tuple(str(x) for x in edges), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_call_graph(obj: CallGraph) -> bool:
    return obj.valid()
