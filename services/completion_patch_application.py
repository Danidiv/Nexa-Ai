"""Setup 6.93: Patch Application."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class PatchApplication:
    task_id: str
    files: tuple[Any, ...]
    operations: tuple[Any, ...]
    result: tuple[Any, ...]
    digest: str = ""

    def sealed(self) -> "PatchApplication":
        data={"task_id": self.task_id, "files": list(self.files), "operations": list(self.operations), "result": list(self.result)}
        d=_digest(data)
        return PatchApplication(self.task_id, self.files, self.operations, self.result, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "files": list(self.files), "operations": list(self.operations), "result": list(self.result)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_patch_application(task_id: str, files: list[str] | tuple[str,...], operations: list[str] | tuple[str,...], result: list[str] | tuple[str,...]) -> PatchApplication:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(files), tuple(operations), tuple(result)]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return PatchApplication(*values, "").sealed()

def valid_patch_application(obj: PatchApplication) -> bool:
    return isinstance(obj, PatchApplication) and obj.valid()
