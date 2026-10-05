"""Setup 6.4: Integrated Autonomous Software Engineer V2."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class IntegratedAutonomousEngineerV2:
    task_id: str
    capabilities: tuple[str, ...]
    evidence: tuple[str, ...]
    dependencies: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "IntegratedAutonomousEngineerV2":
        data = {'task_id': (self.task_id if not isinstance(self.task_id, tuple) else list(self.task_id)), 'capabilities': (self.capabilities if not isinstance(self.capabilities, tuple) else list(self.capabilities)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence)), 'dependencies': (self.dependencies if not isinstance(self.dependencies, tuple) else list(self.dependencies))}
        return IntegratedAutonomousEngineerV2(self.task_id, self.capabilities, self.evidence, self.dependencies, _digest(data))

    def valid(self) -> bool:
        data = {'task_id': (self.task_id if not isinstance(self.task_id, tuple) else list(self.task_id)), 'capabilities': (self.capabilities if not isinstance(self.capabilities, tuple) else list(self.capabilities)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence)), 'dependencies': (self.dependencies if not isinstance(self.dependencies, tuple) else list(self.dependencies))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_integrated_autonomous_engineer_v2(task_id: str, capabilities: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...], dependencies: list[str] | tuple[str, ...]) -> IntegratedAutonomousEngineerV2:
    if isinstance(task_id, str) and not task_id.strip(): raise ValueError("task_id is required")
    if len(capabilities) > 128: raise ValueError("capabilities is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    if len(dependencies) > 128: raise ValueError("dependencies is bounded to 128")
    return IntegratedAutonomousEngineerV2(task_id.strip(), tuple(str(x) for x in capabilities), tuple(str(x) for x in evidence), tuple(str(x) for x in dependencies)).sealed()

def valid_integrated_autonomous_engineer_v2(obj: IntegratedAutonomousEngineerV2) -> bool:
    return obj.valid()
