"""Setup 6.01: Codebase Semantic Map."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class CodebaseSemanticMap:
    name: str
    nodes: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "CodebaseSemanticMap":
        data = {"name": self.name, "nodes": list(self.nodes), "evidence": list(self.evidence)}
        return CodebaseSemanticMap(self.name, self.nodes, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "nodes": list(self.nodes), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_codebase_semantic_map(name: str, nodes: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> CodebaseSemanticMap:
    if not name.strip():
        raise ValueError("name is required")
    if len(nodes) > 128:
        raise ValueError("nodes are bounded to 128")
    if len(evidence) > 128:
        raise ValueError("evidence is bounded to 128")
    obj = CodebaseSemanticMap(name.strip(), tuple(str(x) for x in nodes), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_codebase_semantic_map(obj: CodebaseSemanticMap) -> bool:
    return obj.valid()
