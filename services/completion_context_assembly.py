"""Setup 6.22: Context Assembly."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class ContextAssembly:
    task_id: str
    sources: tuple[str, ...]
    budget: dict[str, Any]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "ContextAssembly":
        data = {'task_id': (self.task_id if not isinstance(self.task_id, tuple) else list(self.task_id)), 'sources': (self.sources if not isinstance(self.sources, tuple) else list(self.sources)), 'budget': (self.budget if not isinstance(self.budget, tuple) else list(self.budget)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return ContextAssembly(self.task_id, self.sources, self.budget, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'task_id': (self.task_id if not isinstance(self.task_id, tuple) else list(self.task_id)), 'sources': (self.sources if not isinstance(self.sources, tuple) else list(self.sources)), 'budget': (self.budget if not isinstance(self.budget, tuple) else list(self.budget)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_context_assembly(task_id: str, sources: list[str] | tuple[str, ...], budget: dict[str, Any], evidence: list[str] | tuple[str, ...]) -> ContextAssembly:
    if isinstance(task_id, str) and not task_id.strip(): raise ValueError("task_id is required")
    if len(sources) > 128: raise ValueError("sources is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return ContextAssembly(task_id.strip(), tuple(str(x) for x in sources), budget, tuple(str(x) for x in evidence)).sealed()

def valid_context_assembly(obj: ContextAssembly) -> bool:
    return obj.valid()
