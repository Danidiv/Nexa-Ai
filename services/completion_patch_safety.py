"""Setup 6.92: Patch Safety."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class PatchSafety:
    task_id: str
    files: tuple[Any, ...]
    checks: tuple[Any, ...]
    risk: tuple[Any, ...]
    digest: str = ""

    def sealed(self) -> "PatchSafety":
        data={"task_id": self.task_id, "files": list(self.files), "checks": list(self.checks), "risk": list(self.risk)}
        d=_digest(data)
        return PatchSafety(self.task_id, self.files, self.checks, self.risk, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "files": list(self.files), "checks": list(self.checks), "risk": list(self.risk)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_patch_safety(task_id: str, files: list[str] | tuple[str,...], checks: list[str] | tuple[str,...], risk: list[str] | tuple[str,...]) -> PatchSafety:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(files), tuple(checks), tuple(risk)]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return PatchSafety(*values, "").sealed()

def valid_patch_safety(obj: PatchSafety) -> bool:
    return isinstance(obj, PatchSafety) and obj.valid()
