"""Setup 6.13: API Contract Inference."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class ApiContractInference:
    name: str
    contracts: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    digest: str = ""

    def sealed(self) -> "ApiContractInference":
        data = {"name": self.name, "contracts": list(self.contracts), "evidence": list(self.evidence)}
        return ApiContractInference(self.name, self.contracts, self.evidence, _digest(data))

    def valid(self) -> bool:
        data = {"name": self.name, "contracts": list(self.contracts), "evidence": list(self.evidence)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_api_contract_inference(name: str, contracts: list[str] | tuple[str, ...], evidence: list[str] | tuple[str, ...] = ()) -> ApiContractInference:
    if not name.strip(): raise ValueError("name is required")
    if len(contracts) > 128: raise ValueError("contracts are bounded to 128")
    if len(evidence) > 128: raise ValueError("evidence is bounded to 128")
    return ApiContractInference(name.strip(), tuple(str(x) for x in contracts), tuple(str(x) for x in evidence)).sealed()

def valid_api_contract_inference(obj: ApiContractInference) -> bool:
    return obj.valid()
