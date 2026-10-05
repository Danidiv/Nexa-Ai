"""Setup 6.27: Test Execution Orchestration."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class TestExecutionOrchestration:
    commands: tuple[str, ...]
    stages: tuple[str, ...]
    limits: dict[str, Any]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "TestExecutionOrchestration":
        data = {'commands': (self.commands if not isinstance(self.commands, tuple) else list(self.commands)), 'stages': (self.stages if not isinstance(self.stages, tuple) else list(self.stages)), 'limits': (self.limits if not isinstance(self.limits, tuple) else list(self.limits)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return TestExecutionOrchestration(self.commands, self.stages, self.limits, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'commands': (self.commands if not isinstance(self.commands, tuple) else list(self.commands)), 'stages': (self.stages if not isinstance(self.stages, tuple) else list(self.stages)), 'limits': (self.limits if not isinstance(self.limits, tuple) else list(self.limits)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_test_execution_orchestration(commands: list[str] | tuple[str, ...], stages: list[str] | tuple[str, ...], limits: dict[str, Any], evidence: list[str] | tuple[str, ...]) -> TestExecutionOrchestration:
    if isinstance(commands, str) and not commands.strip(): raise ValueError("commands is required")
    if len(commands) > 128: raise ValueError("commands is bounded to 128")
    if len(stages) > 128: raise ValueError("stages is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return TestExecutionOrchestration(tuple(str(x) for x in commands), tuple(str(x) for x in stages), limits, tuple(str(x) for x in evidence)).sealed()

def valid_test_execution_orchestration(obj: TestExecutionOrchestration) -> bool:
    return obj.valid()
