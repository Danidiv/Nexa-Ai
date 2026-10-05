"""Setup 4.59: tamper-evident, one-time completion finalization locks."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
import uuid
from typing import Any

VERSION = 1


def _norm(value: Any) -> str:
    return str(value or "").strip()


def _digest(value: Any) -> str:
    text = _norm(value)
    if not text:
        return ""
    return sha256(text.encode("utf-8", errors="replace")).hexdigest()[:24]


def _payload(record: "CompletionFinalization") -> dict[str, Any]:
    return {
        "version": VERSION,
        "finalization_id": record.finalization_id,
        "receipt_id": record.receipt_id,
        "receipt_seal_digest": record.receipt_seal_digest,
        "conversation_id_digest": record.conversation_id_digest,
        "task_digest": record.task_digest,
        "answer_digest": record.answer_digest,
        "change_epoch": max(0, int(record.change_epoch or 0)),
        "finalized": bool(record.finalized),
    }


def _seal(record: "CompletionFinalization") -> str:
    encoded = json.dumps(_payload(record), sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


@dataclass
class CompletionFinalization:
    status: str = "not_required"
    finalization_id: str = ""
    receipt_id: str = ""
    receipt_seal_digest: str = ""
    conversation_id_digest: str = ""
    task_digest: str = ""
    answer_digest: str = ""
    change_epoch: int = 0
    finalized: bool = False
    seal: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["finalization_version"] = VERSION
        data["change_epoch"] = max(0, int(self.change_epoch or 0))
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionFinalization | None":
        if not isinstance(data, dict):
            return None
        if data.get("finalization_version", VERSION) != VERSION:
            return None
        status = str(data.get("status", "not_required") or "not_required")
        if status not in {"not_required", "finalized"}:
            return None
        return cls(
            status=status,
            finalization_id=str(data.get("finalization_id", "") or ""),
            receipt_id=str(data.get("receipt_id", "") or ""),
            receipt_seal_digest=str(data.get("receipt_seal_digest", "") or ""),
            conversation_id_digest=str(data.get("conversation_id_digest", "") or ""),
            task_digest=str(data.get("task_digest", "") or ""),
            answer_digest=str(data.get("answer_digest", "") or ""),
            change_epoch=max(0, int(data.get("change_epoch", 0) or 0)),
            finalized=bool(data.get("finalized", False)),
            seal=str(data.get("seal", "") or ""),
        )

    def valid(self, receipt: Any, conversation_id: Any = "", task_digest: str = "", answer_digest: str = "", change_epoch: int = 0) -> bool:
        if self.status != "finalized" or not self.finalized:
            return False
        if not self.finalization_id or not self.receipt_id or not self.seal:
            return False
        if receipt is None or getattr(receipt, "status", "") != "issued":
            return False
        if _digest(getattr(receipt, "seal", "")) != self.receipt_seal_digest:
            return False
        if _norm(getattr(receipt, "receipt_id", "")) != self.receipt_id:
            return False
        if _digest(conversation_id) != self.conversation_id_digest:
            return False
        if _norm(task_digest) != self.task_digest:
            return False
        if _norm(answer_digest) != self.answer_digest:
            return False
        if max(0, int(change_epoch or 0)) != self.change_epoch:
            return False
        return _seal(self) == self.seal


def issue_completion_finalization(receipt: Any, conversation_id: Any, task_digest: str, answer_digest: str, change_epoch: int) -> CompletionFinalization:
    """Create a finalization lock only from a valid issued completion receipt."""
    if receipt is None or getattr(receipt, "status", "") != "issued":
        return CompletionFinalization()
    receipt_seal = _norm(getattr(receipt, "seal", ""))
    receipt_id = _norm(getattr(receipt, "receipt_id", ""))
    if not receipt_seal or not receipt_id or not _norm(task_digest) or not _norm(answer_digest):
        return CompletionFinalization()
    record = CompletionFinalization(
        status="finalized",
        finalization_id=uuid.uuid4().hex,
        receipt_id=receipt_id,
        receipt_seal_digest=_digest(receipt_seal),
        conversation_id_digest=_digest(conversation_id),
        task_digest=_norm(task_digest),
        answer_digest=_norm(answer_digest),
        change_epoch=max(0, int(change_epoch or 0)),
        finalized=True,
    )
    record.seal = _seal(record)
    return record
