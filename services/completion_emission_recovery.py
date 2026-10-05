"""Setup 4.68: crash-safe reconciliation for terminal emission state."""
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
    if not text:
        return ""
    return sha256(text.encode("utf-8", errors="replace")).hexdigest()[:24]


def _payload(record: "CompletionEmissionRecovery") -> dict[str, Any]:
    return {
        "version": VERSION,
        "status": record.status,
        "recovery_id": record.recovery_id,
        "emission_id": record.emission_id,
        "emission_seal_digest": record.emission_seal_digest,
        "audit_id": record.audit_id,
        "audit_entry_hash": record.audit_entry_hash,
        "conversation_id_digest": record.conversation_id_digest,
        "task_digest": record.task_digest,
        "answer_digest": record.answer_digest,
        "change_epoch": max(0, int(record.change_epoch or 0)),
        "resolved": bool(record.resolved),
    }


def _seal(record: "CompletionEmissionRecovery") -> str:
    encoded = json.dumps(_payload(record), sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


@dataclass
class CompletionEmissionRecovery:
    """Durable reconciliation result for the current terminal emission.

    ``pending`` means a prepared emission exists but has not reached the audit
    history. ``reconciled`` means the emitted emission is present as the latest
    audit record. ``orphaned`` means an emitted marker exists but the audit
    history does not prove it. The recovery record itself never contains raw
    answer text or tool output.
    """

    status: str = "not_required"
    recovery_id: str = ""
    emission_id: str = ""
    emission_seal_digest: str = ""
    audit_id: str = ""
    audit_entry_hash: str = ""
    conversation_id_digest: str = ""
    task_digest: str = ""
    answer_digest: str = ""
    change_epoch: int = 0
    resolved: bool = False
    seal: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["completion_emission_recovery_version"] = VERSION
        data["change_epoch"] = max(0, int(self.change_epoch or 0))
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionEmissionRecovery | None":
        if not isinstance(data, dict):
            return None
        if data.get("completion_emission_recovery_version", VERSION) != VERSION:
            return None
        try:
            return cls(
                status=_norm(data.get("status")) or "not_required",
                recovery_id=_norm(data.get("recovery_id")),
                emission_id=_norm(data.get("emission_id")),
                emission_seal_digest=_norm(data.get("emission_seal_digest")),
                audit_id=_norm(data.get("audit_id")),
                audit_entry_hash=_norm(data.get("audit_entry_hash")),
                conversation_id_digest=_norm(data.get("conversation_id_digest")),
                task_digest=_norm(data.get("task_digest")),
                answer_digest=_norm(data.get("answer_digest")),
                change_epoch=max(0, int(data.get("change_epoch", 0) or 0)),
                resolved=bool(data.get("resolved", False)),
                seal=_norm(data.get("seal")),
            )
        except (TypeError, ValueError):
            return None

    def valid(self) -> bool:
        if self.status == "not_required":
            return not self.recovery_id and not self.seal
        if self.status not in {"pending", "reconciled", "orphaned"}:
            return False
        if not self.recovery_id or not self.emission_id or not self.seal:
            return False
        if self.status == "pending" and self.resolved:
            return False
        if self.status in {"reconciled", "orphaned"} and not self.resolved:
            return False
        return _seal(self) == self.seal

    def blocks_terminal_emit(self) -> bool:
        return self.status in {"pending", "orphaned"} and not self.resolved

    def matches_context(self, conversation_id: Any, task_digest: str, answer_digest: str, change_epoch: int) -> bool:
        return (
            self.conversation_id_digest == _digest(conversation_id)
            and self.task_digest == _norm(task_digest)
            and self.answer_digest == _norm(answer_digest)
            and self.change_epoch == max(0, int(change_epoch or 0))
        )


def inspect_completion_emission(
    emission: Any,
    audit_trail: Any,
    conversation_id: Any,
    task_digest: str,
    answer_digest: str,
    change_epoch: int,
) -> CompletionEmissionRecovery:
    """Inspect persisted emission state without executing or modifying anything."""
    if emission is None or getattr(emission, "status", "") == "not_required":
        return CompletionEmissionRecovery()

    emission_id = _norm(getattr(emission, "emission_id", ""))
    emission_seal = _digest(getattr(emission, "seal", ""))
    task = _norm(task_digest)
    answer = _norm(answer_digest)
    epoch = max(0, int(change_epoch or 0))
    if not emission_id or not emission_seal or not task or not answer:
        return CompletionEmissionRecovery()

    base = dict(
        recovery_id=sha256((emission_id + emission_seal + task + answer + str(epoch)).encode("utf-8")).hexdigest()[:24],
        emission_id=emission_id,
        emission_seal_digest=emission_seal,
        conversation_id_digest=_digest(conversation_id),
        task_digest=task,
        answer_digest=answer,
        change_epoch=epoch,
    )

    if getattr(emission, "status", "") == "prepared":
        record = CompletionEmissionRecovery(status="pending", **base)
        record.seal = _seal(record)
        return record

    if getattr(emission, "status", "") != "emitted":
        return CompletionEmissionRecovery()

    record = CompletionEmissionRecovery(status="orphaned", **base)
    record.seal = _seal(record)
    return record






def reconcile_emitted(
    emission: Any,
    audit_entry: Any,
    audit_trail: Any,
    conversation_id: Any,
    task_digest: str,
    answer_digest: str,
    change_epoch: int,
) -> CompletionEmissionRecovery:
    """Create a durable reconciled/orphaned result after audit append."""
    if emission is None or getattr(emission, "status", "") != "emitted":
        return CompletionEmissionRecovery()
    if audit_entry is None or audit_trail is None or not audit_trail.integrity_valid():
        record = CompletionEmissionRecovery(
            status="orphaned",
            recovery_id=sha256((_norm(getattr(emission, "emission_id", "")) + "orphan").encode()).hexdigest()[:24],
            emission_id=_norm(getattr(emission, "emission_id", "")),
            emission_seal_digest=_digest(getattr(emission, "seal", "")),
            conversation_id_digest=_digest(conversation_id),
            task_digest=_norm(task_digest),
            answer_digest=_norm(answer_digest),
            change_epoch=max(0, int(change_epoch or 0)),
            resolved=True,
        )
        record.seal = _seal(record)
        return record
    if (
        _norm(getattr(audit_entry, "emission_id", "")) != _norm(getattr(emission, "emission_id", ""))
        or _norm(getattr(audit_entry, "emission_seal_digest", "")) != _digest(getattr(emission, "seal", ""))
        or _norm(getattr(audit_entry, "conversation_id_digest", "")) != _digest(conversation_id)
        or _norm(getattr(audit_entry, "task_digest", "")) != _norm(task_digest)
        or _norm(getattr(audit_entry, "answer_digest", "")) != _norm(answer_digest)
        or max(0, int(getattr(audit_entry, "change_epoch", 0) or 0)) != max(0, int(change_epoch or 0))
    ):
        record = CompletionEmissionRecovery(
            status="orphaned",
            recovery_id=sha256((_norm(getattr(emission, "emission_id", "")) + "mismatch").encode()).hexdigest()[:24],
            emission_id=_norm(getattr(emission, "emission_id", "")),
            emission_seal_digest=_digest(getattr(emission, "seal", "")),
            audit_id=_norm(getattr(audit_entry, "audit_id", "")),
            audit_entry_hash=_norm(getattr(audit_entry, "entry_hash", "")),
            conversation_id_digest=_digest(conversation_id),
            task_digest=_norm(task_digest),
            answer_digest=_norm(answer_digest),
            change_epoch=max(0, int(change_epoch or 0)),
            resolved=True,
        )
        record.seal = _seal(record)
        return record

    record = CompletionEmissionRecovery(
        status="reconciled",
        recovery_id=sha256((_norm(getattr(emission, "emission_id", "")) + _norm(getattr(audit_entry, "audit_id", ""))).encode()).hexdigest()[:24],
        emission_id=_norm(getattr(emission, "emission_id", "")),
        emission_seal_digest=_digest(getattr(emission, "seal", "")),
        audit_id=_norm(getattr(audit_entry, "audit_id", "")),
        audit_entry_hash=_norm(getattr(audit_entry, "entry_hash", "")),
        conversation_id_digest=_digest(conversation_id),
        task_digest=_norm(task_digest),
        answer_digest=_norm(answer_digest),
        change_epoch=max(0, int(change_epoch or 0)),
        resolved=True,
    )
    record.seal = _seal(record)
    return record
