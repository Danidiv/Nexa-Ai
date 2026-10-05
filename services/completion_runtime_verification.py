"""Setup 6.96: Runtime Verification."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class RuntimeVerification:
    task_id: str
    entrypoint: str
    checks: tuple[Any, ...]
    observations: tuple[Any, ...]
    digest: str = ""

    def sealed(self) -> "RuntimeVerification":
        data={"task_id": self.task_id, "entrypoint": self.entrypoint, "checks": list(self.checks), "observations": list(self.observations)}
        d=_digest(data)
        return RuntimeVerification(self.task_id, self.entrypoint, self.checks, self.observations, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "entrypoint": self.entrypoint, "checks": list(self.checks), "observations": list(self.observations)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_runtime_verification(task_id: str, entrypoint: str, checks: list[str] | tuple[str,...], observations: list[str] | tuple[str,...]) -> RuntimeVerification:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), entrypoint.strip(), tuple(checks), tuple(observations)]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return RuntimeVerification(*values, "").sealed()

def valid_runtime_verification(obj: RuntimeVerification) -> bool:
    return isinstance(obj, RuntimeVerification) and obj.valid()


# Backward-compatible plan contract used by the older completion/runtime
# integration modules. Kept additive so the newer RuntimeVerification record
# remains the canonical lightweight verification artifact.
@dataclass
class RuntimeVerificationPlan:
    profile: Any
    entrypoints: Any
    environment: Any
    stages: list[dict[str, Any]]
    digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "runtime_verification_plan_version": 1,
            "stages": self.stages,
            "digest": self.digest,
        }

    @classmethod
    def from_dict(cls, d):
        if not isinstance(d, dict) or d.get("runtime_verification_plan_version") != 1:
            return None
        return cls(None, None, None, [dict(x) for x in d.get("stages", [])], str(d.get("digest", "")))

    def valid(self, profile=None, entrypoints=None, environment=None) -> bool:
        payload = {"stages": self.stages}
        return bool(self.digest) and self.digest == _digest(payload)

def build_verification_plan(profile, entrypoints, environment) -> RuntimeVerificationPlan:
    stages = [
        {"name": "static", "description": "static/runtime metadata verification"},
        {"name": "build", "description": "real build/compile verification"},
        {"name": "runtime", "description": "browser/runtime verification"},
    ]
    return RuntimeVerificationPlan(profile, entrypoints, environment, stages, _digest({"stages": stages}))
