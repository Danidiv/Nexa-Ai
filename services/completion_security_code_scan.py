"""Setup 6.15: Security Code Scan."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class SecurityCodeScan:
    name: str
    findings: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "SecurityCodeScan":
        data = {"name": self.name, "findings": list(self.findings), "evidence": list(self.evidence)}
        return SecurityCodeScan(self.name, self.findings, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "findings": list(self.findings), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_security_code_scan(name: str, findings: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> SecurityCodeScan:
    if not name.strip(): raise ValueError("name is required")
    if len(findings) > 128: raise ValueError("findings are bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return SecurityCodeScan(name.strip(), tuple(str(x) for x in findings), tuple(str(x) for x in evidence)).sealed()

def valid_security_code_scan(obj: SecurityCodeScan) -> bool:
    return obj.valid()
