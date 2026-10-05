"""Setup 6.23: Safe Edit Strategy."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class SafeEditStrategy:
    targets: tuple[str, ...]
    strategy: tuple[str, ...]
    guards: tuple[str, ...]
    evidence: tuple[str, ...]
    digest: str = ""

    def sealed(self) -> "SafeEditStrategy":
        data = {'targets': (self.targets if not isinstance(self.targets, tuple) else list(self.targets)), 'strategy': (self.strategy if not isinstance(self.strategy, tuple) else list(self.strategy)), 'guards': (self.guards if not isinstance(self.guards, tuple) else list(self.guards)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return SafeEditStrategy(self.targets, self.strategy, self.guards, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {'targets': (self.targets if not isinstance(self.targets, tuple) else list(self.targets)), 'strategy': (self.strategy if not isinstance(self.strategy, tuple) else list(self.strategy)), 'guards': (self.guards if not isinstance(self.guards, tuple) else list(self.guards)), 'evidence': (self.evidence if not isinstance(self.evidence, tuple) else list(self.evidence))}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_safe_edit_strategy(targets: list[str] | tuple[str, ...], strategy: list[str] | tuple[str, ...], guards: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...]) -> SafeEditStrategy:
    if isinstance(targets, str) and not targets.strip(): raise ValueError("targets is required")
    if len(targets) > 128: raise ValueError("targets is bounded to 128")
    if len(guards) > 128: raise ValueError("guards is bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return SafeEditStrategy(tuple(str(x) for x in targets), tuple(str(x) for x in strategy), tuple(str(x) for x in guards), tuple(str(x) for x in evidence)).sealed()

def valid_safe_edit_strategy(obj: SafeEditStrategy) -> bool:
    return obj.valid()
