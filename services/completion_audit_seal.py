"""Setup 4.61: bind final completion to an immutable audit-trail state."""
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


def audit_trail_digest(audit_trail: Any) -> str:
    if audit_trail is None:
        return ""
    try:
        payload = audit_trail.to_dict()
    except Exception:
        return ""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return _digest(encoded)


def _seal_payload(record: "CompletionAuditSeal") -> dict[str, Any]:
    return {
        "version": VERSION,
        "status": record.status,
        "seal_id": record.seal_id,
        "audit_id": record.audit_id,
        "audit_entry_hash": record.audit_entry_hash,
        "audit_sequence": max(0, int(record.audit_sequence or 0)),
        "audit_anchor_hash": record.audit_anchor_hash,
        "audit_trail_digest": record.audit_trail_digest,
        "conversation_id_digest": record.conversation_id_digest,
        "task_digest": record.task_digest,
        "answer_digest": record.answer_digest,
        "change_epoch": max(0, int(record.change_epoch or 0)),
        "sealed": bool(record.sealed),
    }


def _compute_seal(record: "CompletionAuditSeal") -> str:
    encoded = json.dumps(_seal_payload(record), sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


@dataclass
class CompletionAuditSeal:
    status: str = "not_required"
    seal_id: str = ""
    audit_id: str = ""
    audit_entry_hash: str = ""
    audit_sequence: int = 0
    audit_anchor_hash: str = ""
    audit_trail_digest: str = ""
    conversation_id_digest: str = ""
    task_digest: str = ""
    answer_digest: str = ""
    change_epoch: int = 0
    sealed: bool = False
    seal: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["audit_seal_version"] = VERSION
        data["audit_sequence"] = max(0, int(self.audit_sequence or 0))
        data["change_epoch"] = max(0, int(self.change_epoch or 0))
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionAuditSeal | None":
        if not isinstance(data, dict):
            return None
        if data.get("audit_seal_version", VERSION) != VERSION:
            return None
        return cls(
            status=_norm(data.get("status")) or "not_required",
            seal_id=_norm(data.get("seal_id")),
            audit_id=_norm(data.get("audit_id")),
            audit_entry_hash=_norm(data.get("audit_entry_hash")),
            audit_sequence=max(0, int(data.get("audit_sequence", 0) or 0)),
            audit_anchor_hash=_norm(data.get("audit_anchor_hash")),
            audit_trail_digest=_norm(data.get("audit_trail_digest")),
            conversation_id_digest=_norm(data.get("conversation_id_digest")),
            task_digest=_norm(data.get("task_digest")),
            answer_digest=_norm(data.get("answer_digest")),
            change_epoch=max(0, int(data.get("change_epoch", 0) or 0)),
            sealed=bool(data.get("sealed", False)),
            seal=_norm(data.get("seal")),
        )

    def valid(
        self,
        audit_trail: Any,
        conversation_id: Any,
        task_digest: str,
        answer_digest: str,
        change_epoch: int,
    ) -> bool:
        if self.status != "sealed" or not self.sealed or not self.seal_id or not self.seal:
            return False
        if audit_trail is None or not audit_trail.integrity_valid():
            return False
        latest = audit_trail.latest()
        if latest is None:
            return False
        if self.audit_id != latest.audit_id or self.audit_entry_hash != latest.entry_hash:
            return False
        if self.audit_sequence != latest.sequence:
            return False
        if self.audit_anchor_hash != _norm(getattr(audit_trail, "anchor_hash", "")):
            return False
        if self.audit_trail_digest != audit_trail_digest(audit_trail):
            return False
        if self.conversation_id_digest != _digest(conversation_id):
            return False
        if self.task_digest != _norm(task_digest) or self.answer_digest != _norm(answer_digest):
            return False
        if self.change_epoch != max(0, int(change_epoch or 0)):
            return False
        return _compute_seal(self) == self.seal


def issue_completion_audit_seal(
    audit_trail: Any,
    conversation_id: Any,
    task_digest: str,
    answer_digest: str,
    change_epoch: int,
) -> CompletionAuditSeal:
    if audit_trail is None or not audit_trail.integrity_valid():
        return CompletionAuditSeal()
    latest = audit_trail.latest()
    if latest is None:
        return CompletionAuditSeal()
    if not _norm(task_digest) or not _norm(answer_digest):
        return CompletionAuditSeal()
    record = CompletionAuditSeal(
        status="sealed",
        seal_id=__import__("uuid").uuid4().hex,
        audit_id=_norm(latest.audit_id),
        audit_entry_hash=_norm(latest.entry_hash),
        audit_sequence=max(0, int(latest.sequence or 0)),
        audit_anchor_hash=_norm(getattr(audit_trail, "anchor_hash", "")),
        audit_trail_digest=audit_trail_digest(audit_trail),
        conversation_id_digest=_digest(conversation_id),
        task_digest=_norm(task_digest),
        answer_digest=_norm(answer_digest),
        change_epoch=max(0, int(change_epoch or 0)),
        sealed=True,
    )
    record.seal = _compute_seal(record)
    if not record.valid(audit_trail, conversation_id, task_digest, answer_digest, change_epoch):
        return CompletionAuditSeal()
    return record
