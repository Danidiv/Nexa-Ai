"""Setup 4.64: one-time final-answer release token bound to the terminal proof commitment."""
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


def _payload(record: "CompletionRelease") -> dict[str, Any]:
    return {
        "version": VERSION,
        "status": record.status,
        "release_id": record.release_id,
        "commitment_id": record.commitment_id,
        "commitment_seal_digest": record.commitment_seal_digest,
        "proof_id": record.proof_id,
        "conversation_id_digest": record.conversation_id_digest,
        "task_digest": record.task_digest,
        "answer_digest": record.answer_digest,
        "change_epoch": max(0, int(record.change_epoch or 0)),
        "released": bool(record.released),
        "consumed": bool(record.consumed),
    }


def _compute_seal(record: "CompletionRelease") -> str:
    encoded = json.dumps(_payload(record), sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


@dataclass
class CompletionRelease:
    status: str = "not_required"
    release_id: str = ""
    commitment_id: str = ""
    commitment_seal_digest: str = ""
    proof_id: str = ""
    conversation_id_digest: str = ""
    task_digest: str = ""
    answer_digest: str = ""
    change_epoch: int = 0
    released: bool = False
    consumed: bool = False
    seal: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["completion_release_version"] = VERSION
        data["change_epoch"] = max(0, int(self.change_epoch or 0))
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionRelease | None":
        if not isinstance(data, dict):
            return None
        if data.get("completion_release_version", VERSION) != VERSION:
            return None
        return cls(
            status=_norm(data.get("status")) or "not_required",
            release_id=_norm(data.get("release_id")),
            commitment_id=_norm(data.get("commitment_id")),
            commitment_seal_digest=_norm(data.get("commitment_seal_digest")),
            proof_id=_norm(data.get("proof_id")),
            conversation_id_digest=_norm(data.get("conversation_id_digest")),
            task_digest=_norm(data.get("task_digest")),
            answer_digest=_norm(data.get("answer_digest")),
            change_epoch=max(0, int(data.get("change_epoch", 0) or 0)),
            released=bool(data.get("released", False)),
            consumed=bool(data.get("consumed", False)),
            seal=_norm(data.get("seal")),
        )

    def valid(
        self,
        commitment: Any,
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
        if self.status != "released" or not self.released or self.consumed:
            return False
        if not self.release_id or not self.seal:
            return False
        if commitment is None or getattr(commitment, "status", "") != "committed" or not getattr(commitment, "committed", False):
            return False
        if not commitment.valid(
            proof, attestation, receipt, finalization, audit_trail, audit_seal,
            conversation_id, task_digest, answer_digest, change_epoch,
        ):
            return False
        if self.commitment_id != _norm(getattr(commitment, "commitment_id", "")):
            return False
        if self.commitment_seal_digest != _digest(getattr(commitment, "seal", "")):
            return False
        if self.proof_id != _norm(getattr(proof, "proof_id", "")):
            return False
        if self.conversation_id_digest != _digest(conversation_id):
            return False
        if self.task_digest != _norm(task_digest) or self.answer_digest != _norm(answer_digest):
            return False
        if self.change_epoch != max(0, int(change_epoch or 0)):
            return False
        return _compute_seal(self) == self.seal

    def consume(self) -> bool:
        if not self.released or self.consumed or not self.seal:
            return False
        self.consumed = True
        self.seal = _compute_seal(self)
        return True

    def consumed_valid(
        self,
        commitment: Any,
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
        if self.status != "released" or not self.released or not self.consumed:
            return False
        if not self.release_id or not self.seal:
            return False
        if commitment is None or self.commitment_id != _norm(getattr(commitment, "commitment_id", "")):
            return False
        if not commitment.valid(
            proof, attestation, receipt, finalization, audit_trail, audit_seal,
            conversation_id, task_digest, answer_digest, change_epoch,
        ):
            return False
        if self.commitment_seal_digest != _digest(getattr(commitment, "seal", "")):
            return False
        if proof is None or self.proof_id != _norm(getattr(proof, "proof_id", "")):
            return False
        if self.conversation_id_digest != _digest(conversation_id):
            return False
        if self.task_digest != _norm(task_digest) or self.answer_digest != _norm(answer_digest):
            return False
        if self.change_epoch != max(0, int(change_epoch or 0)):
            return False
        return _compute_seal(self) == self.seal


def issue_completion_release(
    commitment: Any,
    proof: Any,
    conversation_id: Any,
    task_digest: str,
    answer_digest: str,
    change_epoch: int,
) -> CompletionRelease:
    if commitment is None or getattr(commitment, "status", "") != "committed" or not getattr(commitment, "committed", False):
        return CompletionRelease()
    if proof is None or getattr(proof, "status", "") != "sealed" or not getattr(proof, "sealed", False):
        return CompletionRelease()
    values = [
        getattr(commitment, "commitment_id", ""),
        getattr(commitment, "seal", ""),
        getattr(proof, "proof_id", ""),
        _digest(conversation_id), _norm(task_digest), _norm(answer_digest),
    ]
    if not all(values):
        return CompletionRelease()
    record = CompletionRelease(
        status="released",
        release_id=uuid.uuid4().hex,
        commitment_id=_norm(getattr(commitment, "commitment_id", "")),
        commitment_seal_digest=_digest(getattr(commitment, "seal", "")),
        proof_id=_norm(getattr(proof, "proof_id", "")),
        conversation_id_digest=_digest(conversation_id),
        task_digest=_norm(task_digest),
        answer_digest=_norm(answer_digest),
        change_epoch=max(0, int(change_epoch or 0)),
        released=True,
    )
    record.seal = _compute_seal(record)
    return record
