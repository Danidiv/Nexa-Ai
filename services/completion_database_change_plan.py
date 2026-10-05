"""Setup 6.32: Database Change Planning."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class DatabaseChangePlan:
    changes: tuple[str, ...]
    dependencies: tuple[str, ...]
    rollback: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "DatabaseChangePlan":
        data = {'changes': (self.changes if not isinstance(self.changes, tuple) else list(self.changes)), 'dependencies': (self.dependencies if not isinstance(self.dependencies, tuple) else list(self.dependencies)), 'rollback': (self.rollback if not isinstance(self.rollback, tuple) else list(self.rollback)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return DatabaseChangePlan(self.changes, self.dependencies, self.rollback, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'changes': (self.changes if not isinstance(self.changes, tuple) else list(self.changes)), 'dependencies': (self.dependencies if not isinstance(self.dependencies, tuple) else list(self.dependencies)), 'rollback': (self.rollback if not isinstance(self.rollback, tuple) else list(self.rollback)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_database_change_plan(changes: list[str] | tuple[str, ...], dependencies: list[str] | tuple[str, ...], rollback: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> DatabaseChangePlan:
    if isinstance(changes, str) and not changes.strip(): raise ValueError("changes is required")
    if len(changes) > 128: raise ValueError("changes is bounded to 128")
    if len(dependencies) > 128: raise ValueError("dependencies is bounded to 128")
    if len(rollback) > 128: raise ValueError("rollback is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return DatabaseChangePlan(tuple(str(x) for x in changes), tuple(str(x) for x in dependencies), tuple(str(x) for x in rollback), tuple(str(x) for x in evidence)).sealed()

def valid_database_change_plan(obj: DatabaseChangePlan) -> bool:
    return obj.valid()
