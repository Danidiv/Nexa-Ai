"""Setup 6.26: Test Generation Planning."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class TestGenerationPlan:
    targets: tuple[str, ...]
    framework: tuple[str, ...]
    cases: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "TestGenerationPlan":
        data = {'targets': (self.targets if not isinstance(self.targets, tuple) else list(self.targets)), 'framework': (self.framework if not isinstance(self.framework, tuple) else list(self.framework)), 'cases': (self.cases if not isinstance(self.cases, tuple) else list(self.cases)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return TestGenerationPlan(self.targets, self.framework, self.cases, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'targets': (self.targets if not isinstance(self.targets, tuple) else list(self.targets)), 'framework': (self.framework if not isinstance(self.framework, tuple) else list(self.framework)), 'cases': (self.cases if not isinstance(self.cases, tuple) else list(self.cases)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_test_generation_plan(targets: list[str] | tuple[str, ...], framework: list[str] | tuple[str, ...], cases: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> TestGenerationPlan:
    if isinstance(targets, str) and not targets.strip(): raise ValueError("targets is required")
    if len(targets) > 128: raise ValueError("targets is bounded to 128")
    if len(cases) > 128: raise ValueError("cases is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return TestGenerationPlan(tuple(str(x) for x in targets), tuple(str(x) for x in framework), tuple(str(x) for x in cases), tuple(str(x) for x in evidence)).sealed()

def valid_test_generation_plan(obj: TestGenerationPlan) -> bool:
    return obj.valid()
