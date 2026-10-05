"""Setup 6.37: Git Change Set Planning."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class GitChangeSetPlan:
    files: tuple[str, ...]
    changes: tuple[str, ...]
    checks: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "GitChangeSetPlan":
        data = {'files': (self.files if not isinstance(self.files, tuple) else list(self.files)), 'changes': (self.changes if not isinstance(self.changes, tuple) else list(self.changes)), 'checks': (self.checks if not isinstance(self.checks, tuple) else list(self.checks)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return GitChangeSetPlan(self.files, self.changes, self.checks, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'files': (self.files if not isinstance(self.files, tuple) else list(self.files)), 'changes': (self.changes if not isinstance(self.changes, tuple) else list(self.changes)), 'checks': (self.checks if not isinstance(self.checks, tuple) else list(self.checks)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_git_change_set_plan(files: list[str] | tuple[str, ...], changes: list[str] | tuple[str, ...], checks: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> GitChangeSetPlan:
    if isinstance(files, str) and not files.strip(): raise ValueError("files is required")
    if len(files) > 128: raise ValueError("files is bounded to 128")
    if len(changes) > 128: raise ValueError("changes is bounded to 128")
    if len(checks) > 128: raise ValueError("checks is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return GitChangeSetPlan(tuple(str(x) for x in files), tuple(str(x) for x in changes), tuple(str(x) for x in checks), tuple(str(x) for x in evidence)).sealed()

def valid_git_change_set_plan(obj: GitChangeSetPlan) -> bool:
    return obj.valid()
