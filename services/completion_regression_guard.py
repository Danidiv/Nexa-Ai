"""Setup 6.3: Regression Guard."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class RegressionGuard:
    baseline: tuple[str, ...]
    checks: tuple[str, ...]
    thresholds: dict[str, Any]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "RegressionGuard":
        data = {'baseline': (self.baseline if not isinstance(self.baseline, tuple) else list(self.baseline)), 'checks': (self.checks if not isinstance(self.checks, tuple) else list(self.checks)), 'thresholds': (self.thresholds if not isinstance(self.thresholds, tuple) else list(self.thresholds)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return RegressionGuard(self.baseline, self.checks, self.thresholds, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'baseline': (self.baseline if not isinstance(self.baseline, tuple) else list(self.baseline)), 'checks': (self.checks if not isinstance(self.checks, tuple) else list(self.checks)), 'thresholds': (self.thresholds if not isinstance(self.thresholds, tuple) else list(self.thresholds)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_regression_guard(baseline: list[str] | tuple[str, ...], checks: list[str] | tuple[str, ...], thresholds: dict[str, Any], evidence: list[str] | tuple[str, ...]) -> RegressionGuard:
    if isinstance(baseline, str) and not baseline.strip(): raise ValueError("baseline is required")
    if len(checks) > 128: raise ValueError("checks is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return RegressionGuard(tuple(str(x) for x in baseline), tuple(str(x) for x in checks), thresholds, tuple(str(x) for x in evidence)).sealed()

def valid_regression_guard(obj: RegressionGuard) -> bool:
    return obj.valid()
