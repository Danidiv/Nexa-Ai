"""Setup 5.97: Data Migration Readiness."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class DataMigrationReadiness:
    name: str
    migrations: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "DataMigrationReadiness":
        data = {"name": self.name, "migrations": list(self.migrations), "evidence": list(self.evidence)}
        return DataMigrationReadiness(self.name, self.migrations, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "migrations": list(self.migrations), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_data_migration_readiness(name: str, migrations: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> DataMigrationReadiness:
    if not name.strip():
        raise ValueError("name is required")
    if len(migrations) > 32:
        raise ValueError("migrations are bounded to 32")
    if len(evidence) > 64:
        raise ValueError("evidence is bounded to 64")
    obj = DataMigrationReadiness(name.strip(), tuple(str(x) for x in migrations), tuple(str(x) for x in evidence))
    return obj.sealed()

def valid_data_migration_readiness(obj: DataMigrationReadiness) -> bool:
    return obj.valid()
