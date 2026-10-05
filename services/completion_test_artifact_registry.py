"""Setup 5.547: Test Artifact Registry.

indexes QA artifacts and their provenance.
"""
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any, Dict, List

@dataclass(frozen=True)
class TestArtifactRegistry:
    payload: Dict[str, Any]
    digest: str

def _digest(payload: Dict[str, Any]) -> str:
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True)
    return hashlib.sha256(raw.encode()).hexdigest()

def build_test_artifact_registry(**kwargs) -> TestArtifactRegistry:
    payload={"setup":"5.547","kind":"Test Artifact Registry","data":kwargs}
    return TestArtifactRegistry(payload=payload,digest=_digest(payload))

def valid_test_artifact_registry(item: TestArtifactRegistry) -> bool:
    return bool(item.digest) and item.digest == _digest(item.payload)
