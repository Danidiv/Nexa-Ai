"""Setup 6.21: Code Generation Planning."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class CodeGenerationPlan:
    request: str
    constraints: tuple[str, ...]
    targets: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "CodeGenerationPlan":
        data = {'request': (self.request if not isinstance(self.request, tuple) else list(self.request)), 'constraints': (self.constraints if not isinstance(self.constraints, tuple) else list(self.constraints)), 'targets': (self.targets if not isinstance(self.targets, tuple) else list(self.targets)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return CodeGenerationPlan(self.request, self.constraints, self.targets, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'request': (self.request if not isinstance(self.request, tuple) else list(self.request)), 'constraints': (self.constraints if not isinstance(self.constraints, tuple) else list(self.constraints)), 'targets': (self.targets if not isinstance(self.targets, tuple) else list(self.targets)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_code_generation_plan(request: str, constraints: list[str] | tuple[str, ...], targets: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> CodeGenerationPlan:
    if isinstance(request, str) and not request.strip(): raise ValueError("request is required")
    if len(constraints) > 128: raise ValueError("constraints is bounded to 128")
    if len(targets) > 128: raise ValueError("targets is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return CodeGenerationPlan(request.strip(), tuple(str(x) for x in constraints), tuple(str(x) for x in targets), tuple(str(x) for x in evidence)).sealed()

def valid_code_generation_plan(obj: CodeGenerationPlan) -> bool:
    return obj.valid()
