"""Setup 6.94: Post-Patch Validation."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class PostPatchValidation:
    task_id: str
    checks: tuple[Any, ...]
    results: tuple[Any, ...]
    status: str
    digest: str = ""

    def sealed(self) -> "PostPatchValidation":
        data={"task_id": self.task_id, "checks": list(self.checks), "results": list(self.results), "status": self.status}
        d=_digest(data)
        return PostPatchValidation(self.task_id, self.checks, self.results, self.status, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "checks": list(self.checks), "results": list(self.results), "status": self.status}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_post_patch_validation(task_id: str, checks: list[str] | tuple[str,...], results: list[str] | tuple[str,...], status: str) -> PostPatchValidation:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(checks), tuple(results), status.strip()]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return PostPatchValidation(*values, "").sealed()

def valid_post_patch_validation(obj: PostPatchValidation) -> bool:
    return isinstance(obj, PostPatchValidation) and obj.valid()
