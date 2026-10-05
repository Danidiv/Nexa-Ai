"""Setup 6.25: Syntax Repair Planning."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class SyntaxRepairPlan:
    failures: tuple[str, ...]
    repairs: tuple[str, ...]
    validation: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "SyntaxRepairPlan":
        data = {'failures': (self.failures if not isinstance(self.failures, tuple) else list(self.failures)), 'repairs': (self.repairs if not isinstance(self.repairs, tuple) else list(self.repairs)), 'validation': (self.validation if not isinstance(self.validation, tuple) else list(self.validation)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return SyntaxRepairPlan(self.failures, self.repairs, self.validation, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'failures': (self.failures if not isinstance(self.failures, tuple) else list(self.failures)), 'repairs': (self.repairs if not isinstance(self.repairs, tuple) else list(self.repairs)), 'validation': (self.validation if not isinstance(self.validation, tuple) else list(self.validation)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_syntax_repair_plan(failures: list[str] | tuple[str, ...], repairs: list[str] | tuple[str, ...], validation: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> SyntaxRepairPlan:
    if isinstance(failures, str) and not failures.strip(): raise ValueError("failures is required")
    if len(failures) > 128: raise ValueError("failures is bounded to 128")
    if len(repairs) > 128: raise ValueError("repairs is bounded to 128")
    if len(validation) > 128: raise ValueError("validation is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return SyntaxRepairPlan(tuple(str(x) for x in failures), tuple(str(x) for x in repairs), tuple(str(x) for x in validation), tuple(str(x) for x in evidence)).sealed()

def valid_syntax_repair_plan(obj: SyntaxRepairPlan) -> bool:
    return obj.valid()
