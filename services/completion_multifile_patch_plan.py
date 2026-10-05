"""Setup 6.24: Multi-File Patch Planning."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class MultiFilePatchPlan:
    files: tuple[str, ...]
    operations: tuple[str, ...]
    order: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "MultiFilePatchPlan":
        data = {'files': (self.files if not isinstance(self.files, tuple) else list(self.files)), 'operations': (self.operations if not isinstance(self.operations, tuple) else list(self.operations)), 'order': (self.order if not isinstance(self.order, tuple) else list(self.order)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return MultiFilePatchPlan(self.files, self.operations, self.order, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'files': (self.files if not isinstance(self.files, tuple) else list(self.files)), 'operations': (self.operations if not isinstance(self.operations, tuple) else list(self.operations)), 'order': (self.order if not isinstance(self.order, tuple) else list(self.order)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_multifile_patch_plan(files: list[str] | tuple[str, ...], operations: list[str] | tuple[str, ...], order: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> MultiFilePatchPlan:
    if isinstance(files, str) and not files.strip(): raise ValueError("files is required")
    if len(files) > 128: raise ValueError("files is bounded to 128")
    if len(operations) > 128: raise ValueError("operations is bounded to 128")
    if len(order) > 128: raise ValueError("order is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return MultiFilePatchPlan(tuple(str(x) for x in files), tuple(str(x) for x in operations), tuple(str(x) for x in order), tuple(str(x) for x in evidence)).sealed()

def valid_multifile_patch_plan(obj: MultiFilePatchPlan) -> bool:
    return obj.valid()
