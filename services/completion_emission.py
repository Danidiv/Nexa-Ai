"""Setup 4.66: durable two-phase terminal answer emission journal."""
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


def _payload(record: "CompletionEmission") -> dict[str, Any]:
    return {
        "version": VERSION,
        "status": record.status,
        "emission_id": record.emission_id,
        "dispatch_id": record.dispatch_id,
        "dispatch_seal_digest": record.dispatch_seal_digest,
        "release_id": record.release_id,
        "commitment_id": record.commitment_id,
        "proof_id": record.proof_id,
        "conversation_id_digest": record.conversation_id_digest,
        "task_digest": record.task_digest,
        "answer_digest": record.answer_digest,
        "change_epoch": max(0, int(record.change_epoch or 0)),
        "prepared": bool(record.prepared),
        "emitted": bool(record.emitted),
    }


def _compute_seal(record: "CompletionEmission") -> str:
    encoded = json.dumps(_payload(record), sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


@dataclass
class CompletionEmission:
    status: str = "not_required"
    emission_id: str = ""
    dispatch_id: str = ""
    dispatch_seal_digest: str = ""
    release_id: str = ""
    commitment_id: str = ""
    proof_id: str = ""
    conversation_id_digest: str = ""
    task_digest: str = ""
    answer_digest: str = ""
    change_epoch: int = 0
    prepared: bool = False
    emitted: bool = False
    seal: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["completion_emission_version"] = VERSION
        data["change_epoch"] = max(0, int(self.change_epoch or 0))
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionEmission | None":
        if not isinstance(data, dict):
            return None
        if data.get("completion_emission_version", VERSION) != VERSION:
            return None
        return cls(
            status=_norm(data.get("status")) or "not_required",
            emission_id=_norm(data.get("emission_id")),
            dispatch_id=_norm(data.get("dispatch_id")),
            dispatch_seal_digest=_norm(data.get("dispatch_seal_digest")),
            release_id=_norm(data.get("release_id")),
            commitment_id=_norm(data.get("commitment_id")),
            proof_id=_norm(data.get("proof_id")),
            conversation_id_digest=_norm(data.get("conversation_id_digest")),
            task_digest=_norm(data.get("task_digest")),
            answer_digest=_norm(data.get("answer_digest")),
            change_epoch=max(0, int(data.get("change_epoch", 0) or 0)),
            prepared=bool(data.get("prepared", False)),
            emitted=bool(data.get("emitted", False)),
            seal=_norm(data.get("seal")),
        )

    def valid_prepared(
        self, dispatch: Any, release: Any, commitment: Any, proof: Any,
        attestation: Any, receipt: Any, finalization: Any, audit_trail: Any,
        audit_seal: Any, conversation_id: Any, task_digest: str,
        answer_digest: str, change_epoch: int,
    ) -> bool:
        if self.status != "prepared" or not self.prepared or self.emitted:
            return False
        if not self.emission_id or not self.seal:
            return False
        if dispatch is None or not dispatch.consumed_valid(
            release, commitment, proof, attestation, receipt, finalization,
            audit_trail, audit_seal, conversation_id, task_digest,
            answer_digest, change_epoch,
        ):
            return False
        if self.dispatch_id != _norm(getattr(dispatch, "dispatch_id", "")):
            return False
        if self.dispatch_seal_digest != _digest(getattr(dispatch, "seal", "")):
            return False
        if self.release_id != _norm(getattr(release, "release_id", "")):
            return False
        if self.commitment_id != _norm(getattr(commitment, "commitment_id", "")):
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

    def mark_emitted(self) -> bool:
        if self.status != "prepared" or not self.prepared or self.emitted or not self.seal:
            return False
        if _compute_seal(self) != self.seal:
            return False
        self.emitted = True
        self.status = "emitted"
        self.seal = _compute_seal(self)
        return True

    def valid_emitted(
        self, dispatch: Any, release: Any, commitment: Any, proof: Any,
        attestation: Any, receipt: Any, finalization: Any, audit_trail: Any,
        audit_seal: Any, conversation_id: Any, task_digest: str,
        answer_digest: str, change_epoch: int,
    ) -> bool:
        if self.status != "emitted" or not self.prepared or not self.emitted:
            return False
        if not self.emission_id or not self.seal:
            return False
        if not dispatch.consumed_valid(
            release, commitment, proof, attestation, receipt, finalization,
            audit_trail, audit_seal, conversation_id, task_digest,
            answer_digest, change_epoch,
        ):
            return False
        if self.dispatch_id != _norm(getattr(dispatch, "dispatch_id", "")):
            return False
        if self.dispatch_seal_digest != _digest(getattr(dispatch, "seal", "")):
            return False
        if self.release_id != _norm(getattr(release, "release_id", "")):
            return False
        if self.commitment_id != _norm(getattr(commitment, "commitment_id", "")):
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


def issue_completion_emission(
    dispatch: Any, release: Any, commitment: Any, proof: Any,
    conversation_id: Any, task_digest: str, answer_digest: str,
    change_epoch: int,
) -> CompletionEmission:
    if dispatch is None or getattr(dispatch, "status", "") != "authorized" or not getattr(dispatch, "consumed", False):
        return CompletionEmission()
    if release is None or not getattr(release, "consumed", False):
        return CompletionEmission()
    if commitment is None or getattr(commitment, "status", "") != "committed":
        return CompletionEmission()
    if proof is None or getattr(proof, "status", "") != "sealed":
        return CompletionEmission()
    values = [
        getattr(dispatch, "dispatch_id", ""), getattr(dispatch, "seal", ""),
        getattr(release, "release_id", ""), getattr(commitment, "commitment_id", ""),
        getattr(proof, "proof_id", ""), _digest(conversation_id),
        _norm(task_digest), _norm(answer_digest),
    ]
    if not all(values):
        return CompletionEmission()
    record = CompletionEmission(
        status="prepared",
        emission_id=uuid.uuid4().hex,
        dispatch_id=_norm(getattr(dispatch, "dispatch_id", "")),
        dispatch_seal_digest=_digest(getattr(dispatch, "seal", "")),
        release_id=_norm(getattr(release, "release_id", "")),
        commitment_id=_norm(getattr(commitment, "commitment_id", "")),
        proof_id=_norm(getattr(proof, "proof_id", "")),
        conversation_id_digest=_digest(conversation_id),
        task_digest=_norm(task_digest),
        answer_digest=_norm(answer_digest),
        change_epoch=max(0, int(change_epoch or 0)),
        prepared=True,
    )
    record.seal = _compute_seal(record)
    return record
