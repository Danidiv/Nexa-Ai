"""Setup 6.85: Edit Plan Validation."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json
from typing import Any

def _digest(payload: dict[str, Any]) -> str:
    body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()

@dataclass(frozen=True)
class EditPlanValidation:
    task_id: str
    edits: tuple[Any, ...]
    preconditions: tuple[Any, ...]
    risks: tuple[Any, ...]
    digest: str = ""

    def sealed(self) -> "EditPlanValidation":
        data={"task_id": self.task_id, "edits": list(self.edits), "preconditions": list(self.preconditions), "risks": list(self.risks)}
        d=_digest(data)
        return EditPlanValidation(self.task_id, self.edits, self.preconditions, self.risks, d)

    def valid(self) -> bool:
        data={"task_id": self.task_id, "edits": list(self.edits), "preconditions": list(self.preconditions), "risks": list(self.risks)}
        return bool(self.digest) and self.digest == _digest(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def build_edit_plan_validation(task_id: str, edits: list[str] | tuple[str,...], preconditions: list[str] | tuple[str,...], risks: list[str] | tuple[str,...]) -> EditPlanValidation:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id is required")
    values=[task_id.strip(), tuple(edits), tuple(preconditions), tuple(risks)]
    for value in values:
        if isinstance(value, tuple) and len(value)>128:
            raise ValueError("contract collections are bounded to 128")
    return EditPlanValidation(*values, "").sealed()

def valid_edit_plan_validation(obj: EditPlanValidation) -> bool:
    return isinstance(obj, EditPlanValidation) and obj.valid()
