"""Setup 4.70: deterministic resolution of terminal emission recovery state.

This module is a policy/decision layer over Setup 4.68 recovery. It never emits,
consumes, or mutates upstream terminal credentials. It converts durable recovery
states into explicit terminal decisions so pending or orphaned emissions cannot
silently reach finalization.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any

VERSION = 1


def _norm(value: Any) -> str:
    return str(value or "").strip()


def _digest(value: Any) -> str:
    text = _norm(value)
    return sha256(text.encode("utf-8", errors="replace")).hexdigest()[:24] if text else ""


def _payload(record: "CompletionEmissionResolution") -> dict[str, Any]:
    return {
        "version": VERSION,
        "status": record.status,
        "resolution_id": record.resolution_id,
        "recovery_id": record.recovery_id,
        "decision": record.decision,
        "reason_code": record.reason_code,
        "emission_id": record.emission_id,
        "audit_id": record.audit_id,
        "conversation_id_digest": record.conversation_id_digest,
        "task_digest": record.task_digest,
        "answer_digest": record.answer_digest,
        "change_epoch": max(0, int(record.change_epoch or 0)),
    }


def _seal(record: "CompletionEmissionResolution") -> str:
    encoded = json.dumps(_payload(record), sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


@dataclass
class CompletionEmissionResolution:
    """Durable decision derived from terminal emission recovery."""

    status: str = "not_required"
    resolution_id: str = ""
    recovery_id: str = ""
    decision: str = ""
    reason_code: str = ""
    emission_id: str = ""
    audit_id: str = ""
    conversation_id_digest: str = ""
    task_digest: str = ""
    answer_digest: str = ""
    change_epoch: int = 0
    seal: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["completion_emission_resolution_version"] = VERSION
        data["change_epoch"] = max(0, int(self.change_epoch or 0))
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionEmissionResolution | None":
        if not isinstance(data, dict):
            return None
        if data.get("completion_emission_resolution_version", VERSION) != VERSION:
            return None
        try:
            return cls(
                status=_norm(data.get("status")) or "not_required",
                resolution_id=_norm(data.get("resolution_id")),
                recovery_id=_norm(data.get("recovery_id")),
                decision=_norm(data.get("decision")),
                reason_code=_norm(data.get("reason_code")),
                emission_id=_norm(data.get("emission_id")),
                audit_id=_norm(data.get("audit_id")),
                conversation_id_digest=_norm(data.get("conversation_id_digest")),
                task_digest=_norm(data.get("task_digest")),
                answer_digest=_norm(data.get("answer_digest")),
                change_epoch=max(0, int(data.get("change_epoch", 0) or 0)),
                seal=_norm(data.get("seal")),
            )
        except (TypeError, ValueError):
            return None

    def valid(self) -> bool:
        if self.status == "not_required":
            return not self.resolution_id and not self.seal
        if self.status not in {"ready", "resume_verification", "quarantine", "invalid"}:
            return False
        if not self.resolution_id or not self.recovery_id or not self.decision or not self.reason_code or not self.seal:
            return False
        return _seal(self) == self.seal

    def blocks_finalization(self) -> bool:
        return self.status in {"resume_verification", "quarantine", "invalid"}

    def requires_fresh_completion(self) -> bool:
        return self.status in {"quarantine", "invalid"}

    def matches_context(self, conversation_id: Any, task_digest: str, answer_digest: str, change_epoch: int) -> bool:
        return (
            self.conversation_id_digest == _digest(conversation_id)
            and self.task_digest == _norm(task_digest)
            and self.answer_digest == _norm(answer_digest)
            and self.change_epoch == max(0, int(change_epoch or 0))
        )


def issue_resolution(
    recovery: Any,
    conversation_id: Any | None = None,
    task_digest: str | None = None,
    answer_digest: str | None = None,
    change_epoch: int | None = None,
) -> CompletionEmissionResolution:
    """Resolve a recovery record without modifying the recovery or upstream chain."""
    if recovery is None:
        return CompletionEmissionResolution()

    recovery_valid = bool(getattr(recovery, "valid", lambda: False)())
    status = _norm(getattr(recovery, "status", ""))
    conv = conversation_id if conversation_id is not None else ""
    task = _norm(task_digest) if task_digest is not None else _norm(getattr(recovery, "task_digest", ""))
    answer = _norm(answer_digest) if answer_digest is not None else _norm(getattr(recovery, "answer_digest", ""))
    epoch = max(0, int(change_epoch if change_epoch is not None else getattr(recovery, "change_epoch", 0) or 0))
    conv_digest = _digest(conv) if conversation_id is not None else _norm(getattr(recovery, "conversation_id_digest", ""))
    recovery_id = _norm(getattr(recovery, "recovery_id", ""))
    emission_id = _norm(getattr(recovery, "emission_id", ""))
    audit_id = _norm(getattr(recovery, "audit_id", ""))

    if not recovery_valid:
        decision, reason, result_status = "fresh_completion", "recovery_invalid", "invalid"
    elif status == "not_required":
        return CompletionEmissionResolution()
    elif status == "reconciled":
        decision, reason, result_status = "finalize", "recovery_reconciled", "ready"
    elif status == "pending":
        decision, reason, result_status = "resume_verification", "prepared_emission_pending", "resume_verification"
    elif status == "orphaned":
        decision, reason, result_status = "quarantine", "emitted_without_auditable_reconciliation", "quarantine"
    else:
        decision, reason, result_status = "fresh_completion", "unknown_recovery_status", "invalid"

    seed = "|".join([recovery_id, emission_id, audit_id, conv_digest, task, answer, str(epoch), result_status, decision, reason])
    record = CompletionEmissionResolution(
        status=result_status,
        resolution_id=sha256(seed.encode("utf-8", errors="replace")).hexdigest()[:24],
        recovery_id=recovery_id,
        decision=decision,
        reason_code=reason,
        emission_id=emission_id,
        audit_id=audit_id,
        conversation_id_digest=conv_digest,
        task_digest=task,
        answer_digest=answer,
        change_epoch=epoch,
    )
    record.seal = _seal(record)
    return record
