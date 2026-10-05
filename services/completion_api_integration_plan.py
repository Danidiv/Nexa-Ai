"""Setup 6.31: API Integration Planning."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class ApiIntegrationPlan:
    endpoints: tuple[str, ...]
    contracts: tuple[str, ...]
    adapters: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "ApiIntegrationPlan":
        data = {'endpoints': (self.endpoints if not isinstance(self.endpoints, tuple) else list(self.endpoints)), 'contracts': (self.contracts if not isinstance(self.contracts, tuple) else list(self.contracts)), 'adapters': (self.adapters if not isinstance(self.adapters, tuple) else list(self.adapters)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return ApiIntegrationPlan(self.endpoints, self.contracts, self.adapters, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'endpoints': (self.endpoints if not isinstance(self.endpoints, tuple) else list(self.endpoints)), 'contracts': (self.contracts if not isinstance(self.contracts, tuple) else list(self.contracts)), 'adapters': (self.adapters if not isinstance(self.adapters, tuple) else list(self.adapters)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_api_integration_plan(endpoints: list[str] | tuple[str, ...], contracts: list[str] | tuple[str, ...], adapters: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> ApiIntegrationPlan:
    if isinstance(endpoints, str) and not endpoints.strip(): raise ValueError("endpoints is required")
    if len(endpoints) > 128: raise ValueError("endpoints is bounded to 128")
    if len(contracts) > 128: raise ValueError("contracts is bounded to 128")
    if len(adapters) > 128: raise ValueError("adapters is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return ApiIntegrationPlan(tuple(str(x) for x in endpoints), tuple(str(x) for x in contracts), tuple(str(x) for x in adapters), tuple(str(x) for x in evidence)).sealed()

def valid_api_integration_plan(obj: ApiIntegrationPlan) -> bool:
    return obj.valid()
