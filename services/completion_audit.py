"""Setup 4.60: bounded, tamper-evident audit trail for finalized completions."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
import uuid
from typing import Any

VERSION = 1
MAX_ENTRIES = 32


def _norm(value: Any) -> str:
    return str(value or "").strip()


def _digest(value: Any) -> str:
    text = _norm(value)
    if not text:
        return ""
    return sha256(text.encode("utf-8", errors="replace")).hexdigest()[:24]


def _payload(entry: "CompletionAuditEntry", previous_hash: str) -> dict[str, Any]:
    return {
        "version": VERSION,
        "audit_id": entry.audit_id,
        "sequence": max(0, int(entry.sequence or 0)),
        "finalization_id": entry.finalization_id,
        "receipt_id": entry.receipt_id,
        "finalization_seal_digest": entry.finalization_seal_digest,
        "receipt_seal_digest": entry.receipt_seal_digest,
        "conversation_id_digest": entry.conversation_id_digest,
        "task_digest": entry.task_digest,
        "answer_digest": entry.answer_digest,
        "change_epoch": max(0, int(entry.change_epoch or 0)),
        "issued_at": entry.issued_at,
        "previous_hash": previous_hash,
    }


def _entry_hash(entry: "CompletionAuditEntry", previous_hash: str) -> str:
    encoded = json.dumps(_payload(entry, previous_hash), sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


@dataclass
class CompletionAuditEntry:
    audit_id: str = ""
    sequence: int = 0
    finalization_id: str = ""
    receipt_id: str = ""
    finalization_seal_digest: str = ""
    receipt_seal_digest: str = ""
    conversation_id_digest: str = ""
    task_digest: str = ""
    answer_digest: str = ""
    change_epoch: int = 0
    issued_at: str = ""
    previous_hash: str = ""
    entry_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["change_epoch"] = max(0, int(self.change_epoch or 0))
        data["audit_entry_version"] = VERSION
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionAuditEntry | None":
        if not isinstance(data, dict):
            return None
        if data.get("audit_entry_version", VERSION) != VERSION:
            return None
        return cls(
            audit_id=_norm(data.get("audit_id")),
            sequence=max(0, int(data.get("sequence", 0) or 0)),
            finalization_id=_norm(data.get("finalization_id")),
            receipt_id=_norm(data.get("receipt_id")),
            finalization_seal_digest=_norm(data.get("finalization_seal_digest")),
            receipt_seal_digest=_norm(data.get("receipt_seal_digest")),
            conversation_id_digest=_norm(data.get("conversation_id_digest")),
            task_digest=_norm(data.get("task_digest")),
            answer_digest=_norm(data.get("answer_digest")),
            change_epoch=max(0, int(data.get("change_epoch", 0) or 0)),
            issued_at=_norm(data.get("issued_at")),
            previous_hash=_norm(data.get("previous_hash")),
            entry_hash=_norm(data.get("entry_hash")),
        )


class CompletionAuditTrail:
    """Bounded append-only audit history with a verifiable hash chain."""

    def __init__(self, entries: list[CompletionAuditEntry] | None = None, anchor_hash: str = ""):
        self.entries = list(entries or [])[-MAX_ENTRIES:]
        self.anchor_hash = _norm(anchor_hash)

    def _expected_previous(self, index: int) -> str:
        if index <= 0:
            return self.anchor_hash
        return self.entries[index - 1].entry_hash

    def integrity_valid(self) -> bool:
        if len(self.entries) > MAX_ENTRIES:
            return False
        seen_ids: set[str] = set()
        seen_finalizations: set[str] = set()
        previous = self.anchor_hash
        expected_sequence = 0
        if self.entries:
            expected_sequence = max(0, self.entries[0].sequence)
        for entry in self.entries:
            if not entry.audit_id or entry.audit_id in seen_ids:
                return False
            if not entry.finalization_id or entry.finalization_id in seen_finalizations:
                return False
            if entry.sequence != expected_sequence:
                return False
            if entry.previous_hash != previous:
                return False
            if not entry.entry_hash or _entry_hash(entry, previous) != entry.entry_hash:
                return False
            seen_ids.add(entry.audit_id)
            seen_finalizations.add(entry.finalization_id)
            previous = entry.entry_hash
            expected_sequence += 1
        return True

    def has_finalization(self, finalization_id: Any) -> bool:
        target = _norm(finalization_id)
        return bool(target) and any(entry.finalization_id == target for entry in self.entries)

    def latest(self) -> CompletionAuditEntry | None:
        return self.entries[-1] if self.entries else None

    def append_finalization(
        self,
        finalization: Any,
        receipt: Any,
        conversation_id: Any,
        task_digest: str,
        answer_digest: str,
        change_epoch: int,
    ) -> CompletionAuditEntry | None:
        if finalization is None or not getattr(finalization, "finalized", False):
            return None
        if receipt is None or getattr(receipt, "status", "") != "issued":
            return None
        if not _norm(getattr(finalization, "finalization_id", "")):
            return None
        if self.has_finalization(getattr(finalization, "finalization_id", "")):
            return None
        if not _norm(task_digest) or not _norm(answer_digest):
            return None
        if not self.integrity_valid():
            return None

        sequence = self.entries[-1].sequence + 1 if self.entries else 0
        previous = self.entries[-1].entry_hash if self.entries else self.anchor_hash
        entry = CompletionAuditEntry(
            audit_id=uuid.uuid4().hex,
            sequence=sequence,
            finalization_id=_norm(getattr(finalization, "finalization_id", "")),
            receipt_id=_norm(getattr(receipt, "receipt_id", "")),
            finalization_seal_digest=_digest(getattr(finalization, "seal", "")),
            receipt_seal_digest=_digest(getattr(receipt, "seal", "")),
            conversation_id_digest=_digest(conversation_id),
            task_digest=_norm(task_digest),
            answer_digest=_norm(answer_digest),
            change_epoch=max(0, int(change_epoch or 0)),
            issued_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            previous_hash=previous,
        )
        entry.entry_hash = _entry_hash(entry, previous)

        if len(self.entries) >= MAX_ENTRIES:
            # Preserve the omitted prefix as a compact chain anchor.
            self.anchor_hash = self.entries[0].entry_hash
            self.entries = self.entries[1:]
            entry.sequence = self.entries[-1].sequence + 1 if self.entries else sequence
            entry.previous_hash = self.entries[-1].entry_hash if self.entries else self.anchor_hash
            entry.entry_hash = _entry_hash(entry, entry.previous_hash)

        self.entries.append(entry)
        return entry

    def valid_latest(
        self,
        finalization: Any,
        receipt: Any,
        conversation_id: Any,
        task_digest: str,
        answer_digest: str,
        change_epoch: int,
    ) -> bool:
        if not self.integrity_valid() or not self.entries:
            return False
        entry = self.latest()
        if entry is None:
            return False
        if not getattr(finalization, "finalized", False) or getattr(receipt, "status", "") != "issued":
            return False
        if entry.finalization_id != _norm(getattr(finalization, "finalization_id", "")):
            return False
        if entry.receipt_id != _norm(getattr(receipt, "receipt_id", "")):
            return False
        if entry.finalization_seal_digest != _digest(getattr(finalization, "seal", "")):
            return False
        if entry.receipt_seal_digest != _digest(getattr(receipt, "seal", "")):
            return False
        if entry.conversation_id_digest != _digest(conversation_id):
            return False
        if entry.task_digest != _norm(task_digest):
            return False
        if entry.answer_digest != _norm(answer_digest):
            return False
        if entry.change_epoch != max(0, int(change_epoch or 0)):
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_version": VERSION,
            "max_entries": MAX_ENTRIES,
            "anchor_hash": self.anchor_hash,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionAuditTrail | None":
        if not isinstance(data, dict):
            return None
        if data.get("audit_version", VERSION) != VERSION:
            return None
        raw = data.get("entries", [])
        if not isinstance(raw, list):
            return None
        entries: list[CompletionAuditEntry] = []
        for item in raw[-MAX_ENTRIES:]:
            entry = CompletionAuditEntry.from_dict(item)
            if entry is None:
                return None
            entries.append(entry)
        trail = cls(entries, data.get("anchor_hash", ""))
        return trail
