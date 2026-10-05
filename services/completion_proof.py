"""Setup 4.62: immutable end-to-end completion proof bundle."""
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


def _seal_payload(record: "CompletionProof") -> dict[str, Any]:
    return {
        "version": VERSION,
        "status": record.status,
        "proof_id": record.proof_id,
        "attestation_seal_digest": record.attestation_seal_digest,
        "receipt_id": record.receipt_id,
        "receipt_seal_digest": record.receipt_seal_digest,
        "finalization_id": record.finalization_id,
        "finalization_seal_digest": record.finalization_seal_digest,
        "audit_id": record.audit_id,
        "audit_entry_hash": record.audit_entry_hash,
        "audit_sequence": max(0, int(record.audit_sequence or 0)),
        "audit_seal_id": record.audit_seal_id,
        "audit_seal_digest": record.audit_seal_digest,
        "conversation_id_digest": record.conversation_id_digest,
        "task_digest": record.task_digest,
        "answer_digest": record.answer_digest,
        "change_epoch": max(0, int(record.change_epoch or 0)),
        "sealed": bool(record.sealed),
    }


def _compute_seal(record: "CompletionProof") -> str:
    encoded = json.dumps(_seal_payload(record), sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


@dataclass
class CompletionProof:
    status: str = "not_required"
    proof_id: str = ""
    attestation_seal_digest: str = ""
    receipt_id: str = ""
    receipt_seal_digest: str = ""
    finalization_id: str = ""
    finalization_seal_digest: str = ""
    audit_id: str = ""
    audit_entry_hash: str = ""
    audit_sequence: int = 0
    audit_seal_id: str = ""
    audit_seal_digest: str = ""
    conversation_id_digest: str = ""
    task_digest: str = ""
    answer_digest: str = ""
    change_epoch: int = 0
    sealed: bool = False
    seal: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["completion_proof_version"] = VERSION
        data["audit_sequence"] = max(0, int(self.audit_sequence or 0))
        data["change_epoch"] = max(0, int(self.change_epoch or 0))
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionProof | None":
        if not isinstance(data, dict):
            return None
        if data.get("completion_proof_version", VERSION) != VERSION:
            return None
        return cls(
            status=_norm(data.get("status")) or "not_required",
            proof_id=_norm(data.get("proof_id")),
            attestation_seal_digest=_norm(data.get("attestation_seal_digest")),
            receipt_id=_norm(data.get("receipt_id")),
            receipt_seal_digest=_norm(data.get("receipt_seal_digest")),
            finalization_id=_norm(data.get("finalization_id")),
            finalization_seal_digest=_norm(data.get("finalization_seal_digest")),
            audit_id=_norm(data.get("audit_id")),
            audit_entry_hash=_norm(data.get("audit_entry_hash")),
            audit_sequence=max(0, int(data.get("audit_sequence", 0) or 0)),
            audit_seal_id=_norm(data.get("audit_seal_id")),
            audit_seal_digest=_norm(data.get("audit_seal_digest")),
            conversation_id_digest=_norm(data.get("conversation_id_digest")),
            task_digest=_norm(data.get("task_digest")),
            answer_digest=_norm(data.get("answer_digest")),
            change_epoch=max(0, int(data.get("change_epoch", 0) or 0)),
            sealed=bool(data.get("sealed", False)),
            seal=_norm(data.get("seal")),
        )

    def valid(
        self,
        attestation: Any,
        receipt: Any,
        finalization: Any,
        audit_trail: Any,
        audit_seal: Any,
        conversation_id: Any,
        task_digest: str,
        answer_digest: str,
        change_epoch: int,
    ) -> bool:
        if self.status != "sealed" or not self.sealed or not self.proof_id or not self.seal:
            return False
        if attestation is None or not getattr(attestation, "consumed", False):
            return False
        if receipt is None or getattr(receipt, "status", "") != "issued":
            return False
        if finalization is None or not getattr(finalization, "finalized", False):
            return False
        if audit_trail is None or not audit_trail.integrity_valid():
            return False
        latest = audit_trail.latest()
        if latest is None:
            return False
        if audit_seal is None or not getattr(audit_seal, "sealed", False):
            return False
        if not audit_seal.valid(audit_trail, conversation_id, task_digest, answer_digest, change_epoch):
            return False
        if self.attestation_seal_digest != _digest(getattr(attestation, "seal", "")):
            return False
        if self.receipt_id != _norm(getattr(receipt, "receipt_id", "")):
            return False
        if self.receipt_seal_digest != _digest(getattr(receipt, "seal", "")):
            return False
        if self.finalization_id != _norm(getattr(finalization, "finalization_id", "")):
            return False
        if self.finalization_seal_digest != _digest(getattr(finalization, "seal", "")):
            return False
        if self.audit_id != _norm(latest.audit_id) or self.audit_entry_hash != _norm(latest.entry_hash):
            return False
        if self.audit_sequence != max(0, int(latest.sequence or 0)):
            return False
        if self.audit_seal_id != _norm(getattr(audit_seal, "seal_id", "")):
            return False
        if self.audit_seal_digest != _digest(getattr(audit_seal, "seal", "")):
            return False
        if self.conversation_id_digest != _digest(conversation_id):
            return False
        if self.task_digest != _norm(task_digest) or self.answer_digest != _norm(answer_digest):
            return False
        if self.change_epoch != max(0, int(change_epoch or 0)):
            return False
        return _compute_seal(self) == self.seal


def issue_completion_proof(
    attestation: Any,
    receipt: Any,
    finalization: Any,
    audit_trail: Any,
    audit_seal: Any,
    conversation_id: Any,
    task_digest: str,
    answer_digest: str,
    change_epoch: int,
) -> CompletionProof:
    if attestation is None or not getattr(attestation, "consumed", False):
        return CompletionProof()
    if receipt is None or getattr(receipt, "status", "") != "issued":
        return CompletionProof()
    if finalization is None or not getattr(finalization, "finalized", False):
        return CompletionProof()
    if audit_trail is None or not audit_trail.integrity_valid():
        return CompletionProof()
    latest = audit_trail.latest()
    if latest is None:
        return CompletionProof()
    if audit_seal is None or not getattr(audit_seal, "sealed", False):
        return CompletionProof()
    if not audit_seal.valid(audit_trail, conversation_id, task_digest, answer_digest, change_epoch):
        return CompletionProof()
    record = CompletionProof(
        status="sealed",
        proof_id=uuid.uuid4().hex,
        attestation_seal_digest=_digest(getattr(attestation, "seal", "")),
        receipt_id=_norm(getattr(receipt, "receipt_id", "")),
        receipt_seal_digest=_digest(getattr(receipt, "seal", "")),
        finalization_id=_norm(getattr(finalization, "finalization_id", "")),
        finalization_seal_digest=_digest(getattr(finalization, "seal", "")),
        audit_id=_norm(latest.audit_id),
        audit_entry_hash=_norm(latest.entry_hash),
        audit_sequence=max(0, int(latest.sequence or 0)),
        audit_seal_id=_norm(getattr(audit_seal, "seal_id", "")),
        audit_seal_digest=_digest(getattr(audit_seal, "seal", "")),
        conversation_id_digest=_digest(conversation_id),
        task_digest=_norm(task_digest),
        answer_digest=_norm(answer_digest),
        change_epoch=max(0, int(change_epoch or 0)),
        sealed=True,
    )
    if not all([
        record.attestation_seal_digest,
        record.receipt_id,
        record.receipt_seal_digest,
        record.finalization_id,
        record.finalization_seal_digest,
        record.audit_id,
        record.audit_entry_hash,
        record.audit_seal_id,
        record.audit_seal_digest,
        record.conversation_id_digest,
        record.task_digest,
        record.answer_digest,
    ]):
        return CompletionProof()
    record.seal = _compute_seal(record)
    if not record.valid(attestation, receipt, finalization, audit_trail, audit_seal, conversation_id, task_digest, answer_digest, change_epoch):
        return CompletionProof()
    return record
