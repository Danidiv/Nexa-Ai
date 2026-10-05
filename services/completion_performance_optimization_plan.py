"""Setup 6.35: Performance Optimization Planning."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class PerformanceOptimizationPlan:
    targets: tuple[str, ...]
    budgets: tuple[str, ...]
    actions: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "PerformanceOptimizationPlan":
        data = {'targets': (self.targets if not isinstance(self.targets, tuple) else list(self.targets)), 'budgets': (self.budgets if not isinstance(self.budgets, tuple) else list(self.budgets)), 'actions': (self.actions if not isinstance(self.actions, tuple) else list(self.actions)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return PerformanceOptimizationPlan(self.targets, self.budgets, self.actions, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'targets': (self.targets if not isinstance(self.targets, tuple) else list(self.targets)), 'budgets': (self.budgets if not isinstance(self.budgets, tuple) else list(self.budgets)), 'actions': (self.actions if not isinstance(self.actions, tuple) else list(self.actions)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_performance_optimization_plan(targets: list[str] | tuple[str, ...], budgets: list[str] | tuple[str, ...], actions: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> PerformanceOptimizationPlan:
    if isinstance(targets, str) and not targets.strip(): raise ValueError("targets is required")
    if len(targets) > 128: raise ValueError("targets is bounded to 128")
    if len(actions) > 128: raise ValueError("actions is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return PerformanceOptimizationPlan(tuple(str(x) for x in targets), tuple(str(x) for x in budgets), tuple(str(x) for x in actions), tuple(str(x) for x in evidence)).sealed()

def valid_performance_optimization_plan(obj: PerformanceOptimizationPlan) -> bool:
    return obj.valid()
