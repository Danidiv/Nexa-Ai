"""Setup 5.80: Smoke Test Planning."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any


def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()


@dataclass(frozen=True)
class SmokeTestPlanning:
    name: str
    items: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "SmokeTestPlanning":
        data = {"name": self.name, "items": list(self.items), "evidence": list(self.evidence)}
        return SmokeTestPlanning(self.name, self.items, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "items": list(self.items), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_smoke_test_planning(name: str, items: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> SmokeTestPlanning:
    if not name.strip():
        raise ValueError("name is required")
    if len(items) > 32:
        raise ValueError("items are bounded to 32")
    obj = SmokeTestPlanning(name.strip(), tuple(str(x) for x in items), tuple(str(x) for x in evidence))
    return obj.sealed()


def valid_smoke_test_planning(obj: SmokeTestPlanning) -> bool:
    return obj.valid()
