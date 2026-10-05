"""Setup 6.33: Frontend Backend Coordination."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class FrontendBackendCoordination:
    frontend: tuple[str, ...]
    backend: tuple[str, ...]
    contracts: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "FrontendBackendCoordination":
        data = {'frontend': (self.frontend if not isinstance(self.frontend, tuple) else list(self.frontend)), 'backend': (self.backend if not isinstance(self.backend, tuple) else list(self.backend)), 'contracts': (self.contracts if not isinstance(self.contracts, tuple) else list(self.contracts)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return FrontendBackendCoordination(self.frontend, self.backend, self.contracts, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'frontend': (self.frontend if not isinstance(self.frontend, tuple) else list(self.frontend)), 'backend': (self.backend if not isinstance(self.backend, tuple) else list(self.backend)), 'contracts': (self.contracts if not isinstance(self.contracts, tuple) else list(self.contracts)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_frontend_backend_coordination(frontend: list[str] | tuple[str, ...], backend: list[str] | tuple[str, ...], contracts: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> FrontendBackendCoordination:
    if isinstance(frontend, str) and not frontend.strip(): raise ValueError("frontend is required")
    if len(frontend) > 128: raise ValueError("frontend is bounded to 128")
    if len(backend) > 128: raise ValueError("backend is bounded to 128")
    if len(contracts) > 128: raise ValueError("contracts is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return FrontendBackendCoordination(tuple(str(x) for x in frontend), tuple(str(x) for x in backend), tuple(str(x) for x in contracts), tuple(str(x) for x in evidence)).sealed()

def valid_frontend_backend_coordination(obj: FrontendBackendCoordination) -> bool:
    return obj.valid()
