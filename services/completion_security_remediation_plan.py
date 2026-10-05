"""Setup 6.34: Security Remediation Planning."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class SecurityRemediationPlan:
    findings: tuple[str, ...]
    actions: tuple[str, ...]
    priority: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "SecurityRemediationPlan":
        data = {'findings': (self.findings if not isinstance(self.findings, tuple) else list(self.findings)), 'actions': (self.actions if not isinstance(self.actions, tuple) else list(self.actions)), 'priority': (self.priority if not isinstance(self.priority, tuple) else list(self.priority)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return SecurityRemediationPlan(self.findings, self.actions, self.priority, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'findings': (self.findings if not isinstance(self.findings, tuple) else list(self.findings)), 'actions': (self.actions if not isinstance(self.actions, tuple) else list(self.actions)), 'priority': (self.priority if not isinstance(self.priority, tuple) else list(self.priority)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_security_remediation_plan(findings: list[str] | tuple[str, ...], actions: list[str] | tuple[str, ...], priority: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> SecurityRemediationPlan:
    if isinstance(findings, str) and not findings.strip(): raise ValueError("findings is required")
    if len(findings) > 128: raise ValueError("findings is bounded to 128")
    if len(actions) > 128: raise ValueError("actions is bounded to 128")
    if len(priority) > 128: raise ValueError("priority is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return SecurityRemediationPlan(tuple(str(x) for x in findings), tuple(str(x) for x in actions), tuple(str(x) for x in priority), tuple(str(x) for x in evidence)).sealed()

def valid_security_remediation_plan(obj: SecurityRemediationPlan) -> bool:
    return obj.valid()
