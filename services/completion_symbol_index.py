"""Setup 6.02: Symbol Index."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class SymbolIndex:
    name: str
    symbols: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "SymbolIndex":
        data = {"name": self.name, "symbols": list(self.symbols), "evidence": list(self.evidence)}
        return SymbolIndex(self.name, self.symbols, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "symbols": list(self.symbols), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_symbol_index(name: str, symbols: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> SymbolIndex:
    if not name.strip():
        raise ValueError("name is required")
    if len(symbols) > 128:
        raise ValueError("symbols are bounded to 128")
    if len(evidence) > 128:
        raise ValueError("evidence is bounded to 128")
    obj = SymbolIndex(name.strip(), tuple(str(x) for x in symbols), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_symbol_index(obj: SymbolIndex) -> bool:
    return obj.valid()
