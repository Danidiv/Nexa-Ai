"""Setup 6.82: Repository State Snapshot."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class RepositoryStateSnapshot:
    task_id: str
    files: tuple[Any, ...]
    dependencies: tuple[Any, ...]
    tests: tuple[Any, ...]
    digest: str = ""

    def sealed(self) -> "RepositoryStateSnapshot":
        data={"task_id": self.task_id, "files": list(self.files), "dependencies": list(self.dependencies), "tests": list(self.tests)}
        d=_digest(data)
        return RepositoryStateSnapshot(self.task_id, self.files, self.dependencies, self.tests, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "files": list(self.files), "dependencies": list(self.dependencies), "tests": list(self.tests)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_repository_state_snapshot(task_id: str, files: list[str] | tuple[str,...], dependencies: list[str] | tuple[str,...], tests: list[str] | tuple[str,...]) -> RepositoryStateSnapshot:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(files), tuple(dependencies), tuple(tests)]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return RepositoryStateSnapshot(*values, "").sealed()

def valid_repository_state_snapshot(obj: RepositoryStateSnapshot) -> bool:
    return isinstance(obj, RepositoryStateSnapshot) and obj.valid()
