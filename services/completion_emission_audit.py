"""Setup 4.67: append-only audit history for terminal answer emissions."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
import time
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


def _entry_payload(entry: "CompletionEmissionAuditEntry") -> dict[str, Any]:
    return {
        "version": VERSION,
        "audit_id": entry.audit_id,
        "sequence": max(0, int(entry.sequence or 0)),
        "emission_id": entry.emission_id,
        "emission_seal_digest": entry.emission_seal_digest,
        "dispatch_id": entry.dispatch_id,
        "dispatch_seal_digest": entry.dispatch_seal_digest,
        "release_id": entry.release_id,
        "commitment_id": entry.commitment_id,
        "proof_id": entry.proof_id,
        "conversation_id_digest": entry.conversation_id_digest,
        "task_digest": entry.task_digest,
        "answer_digest": entry.answer_digest,
        "change_epoch": max(0, int(entry.change_epoch or 0)),
        "issued_at": max(0.0, float(entry.issued_at or 0.0)),
        "previous_hash": entry.previous_hash,
    }


def _entry_hash(entry: "CompletionEmissionAuditEntry") -> str:
    encoded = json.dumps(_entry_payload(entry), sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:32]


@dataclass
class CompletionEmissionAuditEntry:
    audit_id: str = ""
    sequence: int = 0
    emission_id: str = ""
    emission_seal_digest: str = ""
    dispatch_id: str = ""
    dispatch_seal_digest: str = ""
    release_id: str = ""
    commitment_id: str = ""
    proof_id: str = ""
    conversation_id_digest: str = ""
    task_digest: str = ""
    answer_digest: str = ""
    change_epoch: int = 0
    issued_at: float = 0.0
    previous_hash: str = ""
    entry_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["completion_emission_audit_entry_version"] = VERSION
        data["sequence"] = max(0, int(self.sequence or 0))
        data["change_epoch"] = max(0, int(self.change_epoch or 0))
        data["issued_at"] = max(0.0, float(self.issued_at or 0.0))
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionEmissionAuditEntry | None":
        if not isinstance(data, dict):
            return None
        if data.get("completion_emission_audit_entry_version", VERSION) != VERSION:
            return None
        try:
            return cls(
                audit_id=_norm(data.get("audit_id")),
                sequence=max(0, int(data.get("sequence", 0) or 0)),
                emission_id=_norm(data.get("emission_id")),
                emission_seal_digest=_norm(data.get("emission_seal_digest")),
                dispatch_id=_norm(data.get("dispatch_id")),
                dispatch_seal_digest=_norm(data.get("dispatch_seal_digest")),
                release_id=_norm(data.get("release_id")),
                commitment_id=_norm(data.get("commitment_id")),
                proof_id=_norm(data.get("proof_id")),
                conversation_id_digest=_norm(data.get("conversation_id_digest")),
                task_digest=_norm(data.get("task_digest")),
                answer_digest=_norm(data.get("answer_digest")),
                change_epoch=max(0, int(data.get("change_epoch", 0) or 0)),
                issued_at=max(0.0, float(data.get("issued_at", 0.0) or 0.0)),
                previous_hash=_norm(data.get("previous_hash")),
                entry_hash=_norm(data.get("entry_hash")),
            )
        except (TypeError, ValueError):
            return None


class CompletionEmissionAuditTrail:
    """Bounded append-only history of successfully emitted terminal answers."""

    def __init__(self, entries: list[CompletionEmissionAuditEntry] | None = None, anchor_hash: str = ""):
        self.entries: list[CompletionEmissionAuditEntry] = list(entries or [])[-MAX_ENTRIES:]
        self.anchor_hash = _norm(anchor_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "completion_emission_audit_version": VERSION,
            "entries": [e.to_dict() for e in self.entries],
            "anchor_hash": self.anchor_hash,
        }

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionEmissionAuditTrail | None":
        if not isinstance(data, dict):
            return None
        if data.get("completion_emission_audit_version", VERSION) != VERSION:
            return None
        raw = data.get("entries", [])
        if not isinstance(raw, list):
            return None
        entries: list[CompletionEmissionAuditEntry] = []
        for item in raw:
            entry = CompletionEmissionAuditEntry.from_dict(item)
            if entry is None:
                return None
            entries.append(entry)
        return cls(entries, data.get("anchor_hash", ""))

    def _next_sequence(self) -> int:
        return (self.entries[-1].sequence + 1) if self.entries else (1 if self.anchor_hash else 1)

    def integrity_valid(self) -> bool:
        if len(self.entries) > MAX_ENTRIES:
            return False
        if not self.entries:
            return True
        expected_prev = self.anchor_hash
        expected_seq = self.entries[0].sequence
        if expected_seq < 1:
            return False
        for entry in self.entries:
            if entry.sequence != expected_seq:
                return False
            if not entry.audit_id or not entry.emission_id or not entry.entry_hash:
                return False
            if entry.previous_hash != expected_prev:
                return False
            if _entry_hash(entry) != entry.entry_hash:
                return False
            expected_prev = entry.entry_hash
            expected_seq += 1
        return True

    def has_emission(self, emission_id: Any) -> bool:
        target = _norm(emission_id)
        return bool(target) and any(e.emission_id == target for e in self.entries)

    def latest(self) -> CompletionEmissionAuditEntry | None:
        return self.entries[-1] if self.entries else None

    def valid_latest(
        self,
        emission: Any,
        dispatch: Any,
        release: Any,
        commitment: Any,
        proof: Any,
        conversation_id: Any,
        task_digest: str,
        answer_digest: str,
        change_epoch: int,
    ) -> bool:
        if not self.integrity_valid() or emission is None or getattr(emission, "status", "") != "emitted":
            return False
        latest = self.latest()
        if latest is None:
            return False
        if latest.emission_id != _norm(getattr(emission, "emission_id", "")):
            return False
        if latest.emission_seal_digest != _digest(getattr(emission, "seal", "")):
            return False
        if latest.dispatch_id != _norm(getattr(dispatch, "dispatch_id", "")):
            return False
        if latest.dispatch_seal_digest != _digest(getattr(dispatch, "seal", "")):
            return False
        if latest.release_id != _norm(getattr(release, "release_id", "")):
            return False
        if latest.commitment_id != _norm(getattr(commitment, "commitment_id", "")):
            return False
        if latest.proof_id != _norm(getattr(proof, "proof_id", "")):
            return False
        if latest.conversation_id_digest != _digest(conversation_id):
            return False
        if latest.task_digest != _norm(task_digest) or latest.answer_digest != _norm(answer_digest):
            return False
        if latest.change_epoch != max(0, int(change_epoch or 0)):
            return False
        return True

    def append_emission(
        self,
        emission: Any,
        dispatch: Any,
        release: Any,
        commitment: Any,
        proof: Any,
        conversation_id: Any,
        task_digest: str,
        answer_digest: str,
        change_epoch: int,
    ) -> CompletionEmissionAuditEntry | None:
        if emission is None or getattr(emission, "status", "") != "emitted" or not getattr(emission, "emitted", False):
            return None
        if dispatch is None or not getattr(dispatch, "consumed", False):
            return None
        if self.has_emission(getattr(emission, "emission_id", "")):
            return None
        if not self.integrity_valid():
            return None
        values = [
            getattr(emission, "emission_id", ""), getattr(emission, "seal", ""),
            getattr(dispatch, "dispatch_id", ""), getattr(dispatch, "seal", ""),
            getattr(release, "release_id", ""), getattr(commitment, "commitment_id", ""),
            getattr(proof, "proof_id", ""), _digest(conversation_id),
            _norm(task_digest), _norm(answer_digest),
        ]
        if not all(values):
            return None
        entry = CompletionEmissionAuditEntry(
            sequence=self._next_sequence(),
            emission_id=_norm(getattr(emission, "emission_id", "")),
            emission_seal_digest=_digest(getattr(emission, "seal", "")),
            dispatch_id=_norm(getattr(dispatch, "dispatch_id", "")),
            dispatch_seal_digest=_digest(getattr(dispatch, "seal", "")),
            release_id=_norm(getattr(release, "release_id", "")),
            commitment_id=_norm(getattr(commitment, "commitment_id", "")),
            proof_id=_norm(getattr(proof, "proof_id", "")),
            conversation_id_digest=_digest(conversation_id),
            task_digest=_norm(task_digest),
            answer_digest=_norm(answer_digest),
            change_epoch=max(0, int(change_epoch or 0)),
            issued_at=time.time(),
            previous_hash=self.entries[-1].entry_hash if self.entries else self.anchor_hash,
        )
        entry.audit_id = sha256((entry.emission_id + entry.dispatch_id + str(entry.sequence) + str(entry.issued_at)).encode()).hexdigest()[:24]
        entry.entry_hash = _entry_hash(entry)
        self.entries.append(entry)
        if len(self.entries) > MAX_ENTRIES:
            dropped = self.entries[:-MAX_ENTRIES]
            self.entries = self.entries[-MAX_ENTRIES:]
            # The new anchor is the hash immediately preceding the retained window.
            self.anchor_hash = self.entries[0].previous_hash
        return entry
