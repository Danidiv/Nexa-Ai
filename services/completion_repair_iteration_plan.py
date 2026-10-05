"""Setup 6.29: Repair Iteration Planning."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class RepairIterationPlan:
    issue_id: str
    iterations: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "RepairIterationPlan":
        data = {'issue_id': (self.issue_id if not isinstance(self.issue_id, tuple) else list(self.issue_id)), 'iterations': (self.iterations if not isinstance(self.iterations, tuple) else list(self.iterations)), 'stop_conditions': (self.stop_conditions if not isinstance(self.stop_conditions, tuple) else list(self.stop_conditions)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return RepairIterationPlan(self.issue_id, self.iterations, self.stop_conditions, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'issue_id': (self.issue_id if not isinstance(self.issue_id, tuple) else list(self.issue_id)), 'iterations': (self.iterations if not isinstance(self.iterations, tuple) else list(self.iterations)), 'stop_conditions': (self.stop_conditions if not isinstance(self.stop_conditions, tuple) else list(self.stop_conditions)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_repair_iteration_plan(issue_id: str, iterations: list[str] | tuple[str, ...], stop_conditions: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> RepairIterationPlan:
    if isinstance(issue_id, str) and not issue_id.strip(): raise ValueError("issue_id is required")
    if len(iterations) > 128: raise ValueError("iterations is bounded to 128")
    if len(stop_conditions) > 128: raise ValueError("stop_conditions is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return RepairIterationPlan(issue_id.strip(), tuple(str(x) for x in iterations), tuple(str(x) for x in stop_conditions), tuple(str(x) for x in evidence)).sealed()

def valid_repair_iteration_plan(obj: RepairIterationPlan) -> bool:
    return obj.valid()
