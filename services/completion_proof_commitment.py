"""Setup 4.63: terminal commitment for the end-to-end completion proof."""
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


def _payload(record: "CompletionProofCommitment") -> dict[str, Any]:
    return {
        "version": VERSION,
        "status": record.status,
        "commitment_id": record.commitment_id,
        "proof_id": record.proof_id,
        "proof_seal_digest": record.proof_seal_digest,
        "audit_seal_id": record.audit_seal_id,
        "audit_seal_digest": record.audit_seal_digest,
        "finalization_id": record.finalization_id,
        "receipt_id": record.receipt_id,
        "conversation_id_digest": record.conversation_id_digest,
        "task_digest": record.task_digest,
        "answer_digest": record.answer_digest,
        "change_epoch": max(0, int(record.change_epoch or 0)),
        "committed": bool(record.committed),
    }


def _compute_seal(record: "CompletionProofCommitment") -> str:
    encoded = json.dumps(_payload(record), sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


@dataclass
class CompletionProofCommitment:
    status: str = "not_required"
    commitment_id: str = ""
    proof_id: str = ""
    proof_seal_digest: str = ""
    audit_seal_id: str = ""
    audit_seal_digest: str = ""
    finalization_id: str = ""
    receipt_id: str = ""
    conversation_id_digest: str = ""
    task_digest: str = ""
    answer_digest: str = ""
    change_epoch: int = 0
    committed: bool = False
    seal: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["completion_proof_commitment_version"] = VERSION
        data["change_epoch"] = max(0, int(self.change_epoch or 0))
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionProofCommitment | None":
        if not isinstance(data, dict):
            return None
        if data.get("completion_proof_commitment_version", VERSION) != VERSION:
            return None
        return cls(
            status=_norm(data.get("status")) or "not_required",
            commitment_id=_norm(data.get("commitment_id")),
            proof_id=_norm(data.get("proof_id")),
            proof_seal_digest=_norm(data.get("proof_seal_digest")),
            audit_seal_id=_norm(data.get("audit_seal_id")),
            audit_seal_digest=_norm(data.get("audit_seal_digest")),
            finalization_id=_norm(data.get("finalization_id")),
            receipt_id=_norm(data.get("receipt_id")),
            conversation_id_digest=_norm(data.get("conversation_id_digest")),
            task_digest=_norm(data.get("task_digest")),
            answer_digest=_norm(data.get("answer_digest")),
            change_epoch=max(0, int(data.get("change_epoch", 0) or 0)),
            committed=bool(data.get("committed", False)),
            seal=_norm(data.get("seal")),
        )

    def valid(
        self,
        proof: Any,
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
        if self.status != "committed" or not self.committed or not self.commitment_id or not self.seal:
            return False
        if proof is None or getattr(proof, "status", "") != "sealed" or not getattr(proof, "sealed", False):
            return False
        if not proof.valid(
            attestation,
            receipt,
            finalization,
            audit_trail,
            audit_seal,
            conversation_id,
            task_digest,
            answer_digest,
            change_epoch,
        ):
            return False
        if self.proof_id != _norm(getattr(proof, "proof_id", "")):
            return False
        if self.proof_seal_digest != _digest(getattr(proof, "seal", "")):
            return False
        if self.audit_seal_id != _norm(getattr(audit_seal, "seal_id", "")):
            return False
        if self.audit_seal_digest != _digest(getattr(audit_seal, "seal", "")):
            return False
        if self.finalization_id != _norm(getattr(finalization, "finalization_id", "")):
            return False
        if self.receipt_id != _norm(getattr(receipt, "receipt_id", "")):
            return False
        if self.conversation_id_digest != _digest(conversation_id):
            return False
        if self.task_digest != _norm(task_digest) or self.answer_digest != _norm(answer_digest):
            return False
        if self.change_epoch != max(0, int(change_epoch or 0)):
            return False
        return _compute_seal(self) == self.seal


def issue_completion_proof_commitment(
    proof: Any,
    audit_seal: Any,
    finalization: Any,
    receipt: Any,
    conversation_id: Any,
    task_digest: str,
    answer_digest: str,
    change_epoch: int,
) -> CompletionProofCommitment:
    if proof is None or getattr(proof, "status", "") != "sealed" or not getattr(proof, "sealed", False):
        return CompletionProofCommitment()
    if not getattr(proof, "proof_id", "") or not getattr(proof, "seal", ""):
        return CompletionProofCommitment()
    if audit_seal is None or not getattr(audit_seal, "sealed", False):
        return CompletionProofCommitment()
    if finalization is None or not getattr(finalization, "finalized", False):
        return CompletionProofCommitment()
    if receipt is None or getattr(receipt, "status", "") != "issued":
        return CompletionProofCommitment()
    record = CompletionProofCommitment(
        status="committed",
        commitment_id=uuid.uuid4().hex,
        proof_id=_norm(getattr(proof, "proof_id", "")),
        proof_seal_digest=_digest(getattr(proof, "seal", "")),
        audit_seal_id=_norm(getattr(audit_seal, "seal_id", "")),
        audit_seal_digest=_digest(getattr(audit_seal, "seal", "")),
        finalization_id=_norm(getattr(finalization, "finalization_id", "")),
        receipt_id=_norm(getattr(receipt, "receipt_id", "")),
        conversation_id_digest=_digest(conversation_id),
        task_digest=_norm(task_digest),
        answer_digest=_norm(answer_digest),
        change_epoch=max(0, int(change_epoch or 0)),
        committed=True,
    )
    if not all([
        record.commitment_id, record.proof_id, record.proof_seal_digest,
        record.audit_seal_id, record.audit_seal_digest,
        record.finalization_id, record.receipt_id,
        record.conversation_id_digest, record.task_digest, record.answer_digest,
    ]):
        return CompletionProofCommitment()
    record.seal = _compute_seal(record)
    return record
