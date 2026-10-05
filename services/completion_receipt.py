"""Setup 4.58: tamper-evident completion receipts bound to consumed attestations."""
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


def conversation_identity_digest(conversation_id: Any) -> str:
    return _digest(conversation_id)


def _receipt_seal_payload(receipt: "CompletionReceipt") -> dict[str, Any]:
    return {
        "version": VERSION,
        "receipt_id": receipt.receipt_id,
        "conversation_id_digest": receipt.conversation_id_digest,
        "task_digest": receipt.task_digest,
        "attestation_seal_digest": receipt.attestation_seal_digest,
        "answer_digest": receipt.answer_digest,
        "change_epoch": max(0, int(receipt.change_epoch or 0)),
    }


def _seal(receipt: "CompletionReceipt") -> str:
    encoded = json.dumps(_receipt_seal_payload(receipt), sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


@dataclass
class CompletionReceipt:
    status: str = "not_required"
    receipt_id: str = ""
    conversation_id_digest: str = ""
    task_digest: str = ""
    attestation_seal_digest: str = ""
    answer_digest: str = ""
    change_epoch: int = 0
    seal: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["receipt_version"] = VERSION
        data["change_epoch"] = max(0, int(self.change_epoch or 0))
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionReceipt | None":
        if not isinstance(data, dict):
            return None
        version = data.get("receipt_version", 1)
        if version != VERSION:
            return None
        status = str(data.get("status", "not_required") or "not_required")
        if status not in {"not_required", "issued"}:
            return None
        return cls(
            status=status,
            receipt_id=str(data.get("receipt_id", "") or ""),
            conversation_id_digest=str(data.get("conversation_id_digest", "") or ""),
            task_digest=str(data.get("task_digest", "") or ""),
            attestation_seal_digest=str(data.get("attestation_seal_digest", "") or ""),
            answer_digest=str(data.get("answer_digest", "") or ""),
            change_epoch=max(0, int(data.get("change_epoch", 0) or 0)),
            seal=str(data.get("seal", "") or ""),
        )

    def valid(self, attestation: Any, conversation_id: Any = "", task_digest: str = "", answer_digest: str = "", change_epoch: int = 0) -> bool:
        if self.status != "issued" or not self.receipt_id or not self.seal:
            return False
        if attestation is None or not getattr(attestation, "consumed", False):
            return False
        if _digest(getattr(attestation, "seal", "")) != self.attestation_seal_digest:
            return False
        expected_conversation = conversation_identity_digest(conversation_id)
        if expected_conversation != self.conversation_id_digest:
            return False
        if _norm(task_digest) != self.task_digest:
            return False
        if _norm(answer_digest) != self.answer_digest:
            return False
        if max(0, int(change_epoch or 0)) != self.change_epoch:
            return False
        return _seal(self) == self.seal


def issue_completion_receipt(attestation: Any, conversation_id: Any, task_digest: str, answer_digest: str, change_epoch: int) -> CompletionReceipt:
    """Issue a receipt only after a completion attestation has been consumed."""
    if attestation is None or not getattr(attestation, "consumed", False):
        return CompletionReceipt()
    if not getattr(attestation, "seal", "") or not _norm(task_digest) or not _norm(answer_digest):
        return CompletionReceipt()
    receipt = CompletionReceipt(
        status="issued",
        receipt_id=uuid.uuid4().hex,
        conversation_id_digest=conversation_identity_digest(conversation_id),
        task_digest=_norm(task_digest),
        attestation_seal_digest=_digest(attestation.seal),
        answer_digest=_norm(answer_digest),
        change_epoch=max(0, int(change_epoch or 0)),
    )
    receipt.seal = _seal(receipt)
    return receipt
