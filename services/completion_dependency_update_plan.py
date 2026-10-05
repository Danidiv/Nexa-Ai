"""Setup 6.36: Dependency Update Planning."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class DependencyUpdatePlan:
    dependencies: tuple[str, ...]
    constraints: tuple[str, ...]
    actions: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "DependencyUpdatePlan":
        data = {'dependencies': (self.dependencies if not isinstance(self.dependencies, tuple) else list(self.dependencies)), 'constraints': (self.constraints if not isinstance(self.constraints, tuple) else list(self.constraints)), 'actions': (self.actions if not isinstance(self.actions, tuple) else list(self.actions)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return DependencyUpdatePlan(self.dependencies, self.constraints, self.actions, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'dependencies': (self.dependencies if not isinstance(self.dependencies, tuple) else list(self.dependencies)), 'constraints': (self.constraints if not isinstance(self.constraints, tuple) else list(self.constraints)), 'actions': (self.actions if not isinstance(self.actions, tuple) else list(self.actions)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_dependency_update_plan(dependencies: list[str] | tuple[str, ...], constraints: list[str] | tuple[str, ...], actions: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> DependencyUpdatePlan:
    if isinstance(dependencies, str) and not dependencies.strip(): raise ValueError("dependencies is required")
    if len(dependencies) > 128: raise ValueError("dependencies is bounded to 128")
    if len(constraints) > 128: raise ValueError("constraints is bounded to 128")
    if len(actions) > 128: raise ValueError("actions is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return DependencyUpdatePlan(tuple(str(x) for x in dependencies), tuple(str(x) for x in constraints), tuple(str(x) for x in actions), tuple(str(x) for x in evidence)).sealed()

def valid_dependency_update_plan(obj: DependencyUpdatePlan) -> bool:
    return obj.valid()
