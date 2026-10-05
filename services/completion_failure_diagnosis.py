"""Setup 6.28: Failure Diagnosis."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class FailureDiagnosis:
    failures: tuple[str, ...]
    causes: tuple[str, ...]
    confidence: dict[str, Any]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "FailureDiagnosis":
        data = {'failures': (self.failures if not isinstance(self.failures, tuple) else list(self.failures)), 'causes': (self.causes if not isinstance(self.causes, tuple) else list(self.causes)), 'confidence': (self.confidence if not isinstance(self.confidence, tuple) else list(self.confidence)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return FailureDiagnosis(self.failures, self.causes, self.confidence, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'failures': (self.failures if not isinstance(self.failures, tuple) else list(self.failures)), 'causes': (self.causes if not isinstance(self.causes, tuple) else list(self.causes)), 'confidence': (self.confidence if not isinstance(self.confidence, tuple) else list(self.confidence)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_failure_diagnosis(failures: list[str] | tuple[str, ...], causes: list[str] | tuple[str, ...], confidence: dict[str, Any], evidence: list[str] | tuple[str, ...]) -> FailureDiagnosis:
    if isinstance(failures, str) and not failures.strip(): raise ValueError("failures is required")
    if len(failures) > 128: raise ValueError("failures is bounded to 128")
    if len(causes) > 128: raise ValueError("causes is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return FailureDiagnosis(tuple(str(x) for x in failures), tuple(str(x) for x in causes), confidence, tuple(str(x) for x in evidence)).sealed()

def valid_failure_diagnosis(obj: FailureDiagnosis) -> bool:
    return obj.valid()
