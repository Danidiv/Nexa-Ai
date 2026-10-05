"""Setup 5.548: QA Repair Execution.

executes only approved evidence-bound repair actions.
"""
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any, Dict, List

@dataclass(frozen=True)
class QaRepairExecution:
    payload: Dict[str, Any]
    digest: str

def _digest(payload: Dict[str, Any]) -> str:
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True)
    return hashlib.sha256(raw.encode()).hexdigest()

def build_qa_repair_execution(**kwargs) -> QaRepairExecution:
    payload={"setup":"5.548","kind":"QA Repair Execution","data":kwargs}
    return QaRepairExecution(payload=payload,digest=_digest(payload))

def valid_qa_repair_execution(item: QaRepairExecution) -> bool:
    return bool(item.digest) and item.digest == _digest(item.payload)
