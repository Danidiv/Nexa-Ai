"""Setup 6.04: Test Discovery."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class TestDiscovery:
    name: str
    tests: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "TestDiscovery":
        data = {"name": self.name, "tests": list(self.tests), "evidence": list(self.evidence)}
        return TestDiscovery(self.name, self.tests, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "tests": list(self.tests), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_test_discovery(name: str, tests: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> TestDiscovery:
    if not name.strip():
        raise ValueError("name is required")
    if len(tests) > 128:
        raise ValueError("tests are bounded to 128")
    if len(evidence) > 128:
        raise ValueError("evidence is bounded to 128")
    obj = TestDiscovery(name.strip(), tuple(str(x) for x in tests), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_test_discovery(obj: TestDiscovery) -> bool:
    return obj.valid()
