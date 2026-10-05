"""Setup 6.84: Implementation Context Selection."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class ImplementationContext:
    task_id: str
    files: tuple[Any, ...]
    symbols: tuple[Any, ...]
    snippets: tuple[Any, ...]
    digest: str = ""

    def sealed(self) -> "ImplementationContext":
        data={"task_id": self.task_id, "files": list(self.files), "symbols": list(self.symbols), "snippets": list(self.snippets)}
        d=_digest(data)
        return ImplementationContext(self.task_id, self.files, self.symbols, self.snippets, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "files": list(self.files), "symbols": list(self.symbols), "snippets": list(self.snippets)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_implementation_context(task_id: str, files: list[str] | tuple[str,...], symbols: list[str] | tuple[str,...], snippets: list[str] | tuple[str,...]) -> ImplementationContext:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(files), tuple(symbols), tuple(snippets)]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return ImplementationContext(*values, "").sealed()

def valid_implementation_context(obj: ImplementationContext) -> bool:
    return isinstance(obj, ImplementationContext) and obj.valid()
