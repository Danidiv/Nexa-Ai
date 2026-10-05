"""Setup 4.65: terminal answer dispatch authorization bound to the consumed release."""
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


def _payload(record: "CompletionDispatch") -> dict[str, Any]:
    return {
        "version": VERSION,
        "status": record.status,
        "dispatch_id": record.dispatch_id,
        "release_id": record.release_id,
        "release_seal_digest": record.release_seal_digest,
        "commitment_id": record.commitment_id,
        "proof_id": record.proof_id,
        "conversation_id_digest": record.conversation_id_digest,
        "task_digest": record.task_digest,
        "answer_digest": record.answer_digest,
        "change_epoch": max(0, int(record.change_epoch or 0)),
        "authorized": bool(record.authorized),
        "consumed": bool(record.consumed),
    }


def _compute_seal(record: "CompletionDispatch") -> str:
    encoded = json.dumps(_payload(record), sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


@dataclass
class CompletionDispatch:
    status: str = "not_required"
    dispatch_id: str = ""
    release_id: str = ""
    release_seal_digest: str = ""
    commitment_id: str = ""
    proof_id: str = ""
    conversation_id_digest: str = ""
    task_digest: str = ""
    answer_digest: str = ""
    change_epoch: int = 0
    authorized: bool = False
    consumed: bool = False
    seal: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["completion_dispatch_version"] = VERSION
        data["change_epoch"] = max(0, int(self.change_epoch or 0))
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionDispatch | None":
        if not isinstance(data, dict):
            return None
        if data.get("completion_dispatch_version", VERSION) != VERSION:
            return None
        return cls(
            status=_norm(data.get("status")) or "not_required",
            dispatch_id=_norm(data.get("dispatch_id")),
            release_id=_norm(data.get("release_id")),
            release_seal_digest=_norm(data.get("release_seal_digest")),
            commitment_id=_norm(data.get("commitment_id")),
            proof_id=_norm(data.get("proof_id")),
            conversation_id_digest=_norm(data.get("conversation_id_digest")),
            task_digest=_norm(data.get("task_digest")),
            answer_digest=_norm(data.get("answer_digest")),
            change_epoch=max(0, int(data.get("change_epoch", 0) or 0)),
            authorized=bool(data.get("authorized", False)),
            consumed=bool(data.get("consumed", False)),
            seal=_norm(data.get("seal")),
        )

    def valid(
        self,
        release: Any,
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
        if self.status != "authorized" or not self.authorized or self.consumed:
            return False
        if not self.dispatch_id or not self.seal:
            return False
        if release is None or not release.consumed_valid(
            commitment, proof, attestation, receipt, finalization, audit_trail, audit_seal,
            conversation_id, task_digest, answer_digest, change_epoch,
        ):
            return False
        if self.release_id != _norm(getattr(release, "release_id", "")):
            return False
        if self.release_seal_digest != _digest(getattr(release, "seal", "")):
            return False
        if commitment is None or self.commitment_id != _norm(getattr(commitment, "commitment_id", "")):
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

    def consume(self) -> bool:
        if not self.authorized or self.consumed or not self.seal:
            return False
        self.consumed = True
        self.seal = _compute_seal(self)
        return True

    def consumed_valid(
        self,
        release: Any,
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
        if self.status != "authorized" or not self.authorized or not self.consumed:
            return False
        if not self.dispatch_id or not self.seal:
            return False
        if release is None or not release.consumed_valid(
            commitment, proof, attestation, receipt, finalization, audit_trail, audit_seal,
            conversation_id, task_digest, answer_digest, change_epoch,
        ):
            return False
        if self.release_id != _norm(getattr(release, "release_id", "")):
            return False
        if self.release_seal_digest != _digest(getattr(release, "seal", "")):
            return False
        if commitment is None or self.commitment_id != _norm(getattr(commitment, "commitment_id", "")):
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


def issue_completion_dispatch(
    release: Any,
    commitment: Any,
    proof: Any,
    conversation_id: Any,
    task_digest: str,
    answer_digest: str,
    change_epoch: int,
) -> CompletionDispatch:
    if release is None or getattr(release, "status", "") != "released" or not getattr(release, "consumed", False):
        return CompletionDispatch()
    if commitment is None or getattr(commitment, "status", "") != "committed" or not getattr(commitment, "committed", False):
        return CompletionDispatch()
    if proof is None or getattr(proof, "status", "") != "sealed" or not getattr(proof, "sealed", False):
        return CompletionDispatch()
    values = [
        getattr(release, "release_id", ""),
        getattr(release, "seal", ""),
        getattr(commitment, "commitment_id", ""),
        getattr(proof, "proof_id", ""),
        _digest(conversation_id), _norm(task_digest), _norm(answer_digest),
    ]
    if not all(values):
        return CompletionDispatch()
    record = CompletionDispatch(
        status="authorized",
        dispatch_id=uuid.uuid4().hex,
        release_id=_norm(getattr(release, "release_id", "")),
        release_seal_digest=_digest(getattr(release, "seal", "")),
        commitment_id=_norm(getattr(commitment, "commitment_id", "")),
        proof_id=_norm(getattr(proof, "proof_id", "")),
        conversation_id_digest=_digest(conversation_id),
        task_digest=_norm(task_digest),
        answer_digest=_norm(answer_digest),
        change_epoch=max(0, int(change_epoch or 0)),
        authorized=True,
    )
    record.seal = _compute_seal(record)
    return record
