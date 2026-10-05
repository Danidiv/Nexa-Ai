"""Setup 4.37: evidence-based completion tracking.

This module records compact, JSON-safe evidence that successful tool actions
actually occurred. It deliberately stores no raw tool output, prompts, or
credentials; result fingerprints are used instead. Completion evidence is
only enforced for tasks that performed modifications and therefore require
post-change verification.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any
import json

from services.evidence_freshness import is_fresh, is_resource_fresh, normalize_epoch, normalize_resource_key, resource_generation

MAX_EVIDENCE = 32
VERSION = 6
CHECKPOINT_VERSION = 1


def _norm(value: Any) -> str:
    return str(value or "").replace("\\", "/").lstrip("./")


def _match(observed: str, required: str) -> bool:
    a, b = _norm(observed), _norm(required)
    return bool(a and b and (a == b or a.endswith("/" + b) or b.endswith("/" + a)))


def _chain_hash(previous_hash: str, evidence: dict[str, Any]) -> str:
    """Return a compact tamper-evident hash for one evidence link."""
    payload = {
        "previous_hash": str(previous_hash or ""),
        "evidence_id": str(evidence.get("evidence_id", "")),
        "action": str(evidence.get("action", "")),
        "category": str(evidence.get("category", "")),
        "path": _norm(evidence.get("path", "")),
        "outcome": str(evidence.get("outcome", "")),
        "fingerprint": str(evidence.get("fingerprint", "")),
        "change_epoch": normalize_epoch(evidence.get("change_epoch", 0)),
        "resource_epoch": normalize_epoch(evidence.get("resource_epoch", 0)),
        "sequence": max(0, int(evidence.get("sequence", 0) or 0)),
        "parent_evidence_id": str(evidence.get("parent_evidence_id", "") or ""),
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


def _checkpoint_hash(entries: list[dict[str, Any]], chain_anchor: str, status: str, missing_requirements: list[str], sequence: int) -> str:
    """Create a deterministic audit checkpoint for the current ledger state."""
    payload = {
        "checkpoint_version": CHECKPOINT_VERSION,
        "entries": [dict(x) for x in entries[:MAX_EVIDENCE] if isinstance(x, dict)],
        "chain_anchor": str(chain_anchor or ""),
        "status": str(status or "not_required"),
        "missing_requirements": [str(x) for x in missing_requirements[:MAX_EVIDENCE]],
        "sequence": max(0, int(sequence or 0)),
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


def _fingerprint(result: Any) -> str:
    try:
        encoded = json.dumps(result, ensure_ascii=False, sort_keys=True, default=str)
    except Exception:
        encoded = str(result)
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:16]


@dataclass
class CompletionEvidence:
    evidence_id: str
    action: str
    category: str
    path: str
    outcome: str
    fingerprint: str
    change_epoch: int = 0
    resource_epoch: int = 0
    sequence: int = 0
    parent_evidence_id: str = ""
    chain_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence_version"] = VERSION
        data["change_epoch"] = normalize_epoch(self.change_epoch)
        data["resource_epoch"] = normalize_epoch(self.resource_epoch)
        data["sequence"] = max(0, int(self.sequence or 0))
        data["parent_evidence_id"] = str(self.parent_evidence_id or "")
        data["chain_hash"] = str(self.chain_hash or "")
        return data


@dataclass
class CompletionEvidenceLedger:
    entries: list[dict[str, Any]]
    status: str
    missing_requirements: list[str]
    chain_anchor: str = ""
    checkpoint_hash: str = ""
    checkpoint_sequence: int = 0
    checkpoint_head_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_version": VERSION,
            "entries": [dict(x) for x in self.entries[:MAX_EVIDENCE] if isinstance(x, dict)],
            "status": self.status,
            "missing_requirements": list(self.missing_requirements[:MAX_EVIDENCE]),
            "chain_anchor": str(self.chain_anchor or ""),
            "checkpoint_version": CHECKPOINT_VERSION,
            "checkpoint_hash": str(self.checkpoint_hash or ""),
            "checkpoint_sequence": max(0, int(self.checkpoint_sequence or 0)),
            "checkpoint_head_hash": str(self.checkpoint_head_hash or ""),
        }

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionEvidenceLedger | None":
        if not isinstance(data, dict) or data.get("evidence_version") not in {1, 2, 3, 4, 5, VERSION}:
            return None
        entries = []
        for item in data.get("entries", []):
            if isinstance(item, dict) and all(k in item for k in ("evidence_version", "evidence_id", "action", "category", "path", "outcome", "fingerprint")):
                entries.append({
                    "evidence_version": VERSION,
                    "evidence_id": str(item["evidence_id"]),
                    "action": str(item["action"]),
                    "category": str(item["category"]),
                    "path": _norm(item["path"]),
                    "outcome": str(item["outcome"]),
                    "fingerprint": str(item["fingerprint"]),
                    "change_epoch": normalize_epoch(item.get("change_epoch", 0)),
                    "resource_epoch": normalize_epoch(item.get("resource_epoch", item.get("change_epoch", 0))),
                    "sequence": max(0, int(item.get("sequence", 0) or 0)),
                    "parent_evidence_id": str(item.get("parent_evidence_id", "") or ""),
                    "chain_hash": str(item.get("chain_hash", "") or ""),
                })
        status = str(data.get("status", "not_required"))
        if status not in {"not_required", "insufficient", "sufficient"}:
            return None
        missing = [str(x) for x in data.get("missing_requirements", []) if isinstance(x, str)]
        return cls(
            entries[:MAX_EVIDENCE],
            status,
            missing[:MAX_EVIDENCE],
            str(data.get("chain_anchor", "") or ""),
            str(data.get("checkpoint_hash", "") or ""),
            max(0, int(data.get("checkpoint_sequence", 0) or 0)),
            str(data.get("checkpoint_head_hash", "") or ""),
        )

    def create_checkpoint(self) -> str:
        """Record an audit checkpoint for the current bounded ledger state."""
        head_hash = str((self.entries[-1] if self.entries else {}).get("chain_hash", "") or "")
        sequence = max([int(e.get("sequence", 0) or 0) for e in self.entries] + [0])
        self.checkpoint_sequence = sequence
        self.checkpoint_head_hash = head_hash
        self.checkpoint_hash = _checkpoint_hash(
            self.entries, self.chain_anchor, self.status, self.missing_requirements, sequence
        )
        return self.checkpoint_hash

    def checkpoint_valid(self) -> bool:
        """Return True when an established checkpoint still matches the ledger."""
        if not self.checkpoint_hash:
            return True
        head_hash = str((self.entries[-1] if self.entries else {}).get("chain_hash", "") or "")
        sequence = max([int(e.get("sequence", 0) or 0) for e in self.entries] + [0])
        if sequence != max(0, int(self.checkpoint_sequence or 0)):
            return False
        if head_hash != str(self.checkpoint_head_hash or ""):
            return False
        expected = _checkpoint_hash(
            self.entries, self.chain_anchor, self.status, self.missing_requirements, sequence
        )
        return expected == str(self.checkpoint_hash)


    def add(self, evidence: CompletionEvidence) -> None:
        # Setup 4.41: maintain a compact provenance chain. Sequence numbers are
        # monotonic within the bounded ledger; verification evidence points to
        # the latest successful modification for the same resource when one exists.
        previous = self.entries[-1] if self.entries else None
        next_sequence = max([int(e.get("sequence", 0) or 0) for e in self.entries] + [0]) + 1
        evidence.sequence = next_sequence
        evidence.parent_evidence_id = str((previous or {}).get("evidence_id", "") or "")
        if evidence.category == "verification":
            target = _norm(evidence.path)
            for item in reversed(self.entries):
                if item.get("category") == "modification" and item.get("outcome") == "success" and _match(item.get("path", ""), target):
                    evidence.parent_evidence_id = str(item.get("evidence_id", "") or evidence.parent_evidence_id)
                    break
        data = evidence.to_dict()
        previous_hash = str((previous or {}).get("chain_hash", "") or "")
        # Setup 4.43: evidence IDs are unique within the bounded ledger.
        # The original evidence ID is content-derived, so repeated identical
        # tool results can legitimately collide. Add a deterministic sequence
        # suffix only when a collision occurs; this prevents replay ambiguity
        # without changing legacy IDs.
        existing_ids = {str(item.get("evidence_id", "") or "") for item in self.entries}
        if str(data.get("evidence_id", "") or "") in existing_ids:
            base_id = str(data.get("evidence_id", "") or "evidence")
            data["evidence_id"] = sha256(
                f"{base_id}|{next_sequence}|{previous_hash}".encode("utf-8", errors="replace")
            ).hexdigest()[:12]
        data["chain_hash"] = _chain_hash(previous_hash, data)
        # Any new evidence invalidates the previous audit boundary until the
        # ledger is evaluated/checkpointed again.
        self.checkpoint_hash = ""
        self.checkpoint_sequence = 0
        self.checkpoint_head_hash = ""
        self.entries.append(data)
        if len(self.entries) > MAX_EVIDENCE:
            dropped = self.entries.pop(0)
            self.chain_anchor = str(dropped.get("chain_hash", "") or "")

    def integrity_valid(self) -> bool:
        """Validate the Setup 4.42 tamper-evident hash chain when present."""
        previous_hash = str(self.chain_anchor or "")
        saw_hash = False
        for item in self.entries:
            stored = str(item.get("chain_hash", "") or "")
            if not stored:
                # Legacy Setup 4.40/4.41 evidence has no hash chain. It remains
                # restorable and usable, but cannot itself prove integrity.
                previous_hash = ""
                continue
            saw_hash = True
            expected = _chain_hash(previous_hash, item)
            if stored != expected:
                return False
            previous_hash = stored
        return True if saw_hash or not self.entries else True

    def provenance_valid(self, required_paths: list[str] | None = None) -> bool:
        """Validate ordering and parent linkage for verification evidence."""
        required = [_norm(x) for x in (required_paths or []) if _norm(x)]
        by_id = {str(e.get("evidence_id")): e for e in self.entries if e.get("evidence_id")}
        last_seq = 0
        for item in self.entries:
            seq = max(0, int(item.get("sequence", 0) or 0))
            if seq and seq <= last_seq:
                return False
            last_seq = max(last_seq, seq)
            parent = str(item.get("parent_evidence_id", "") or "")
            if parent and parent not in by_id:
                return False
            if item.get("category") == "verification" and item.get("outcome") == "success":
                if required and not any(_match(item.get("path", ""), path) for path in required):
                    continue
                matching_modifications = [
                    e for e in self.entries
                    if e.get("category") == "modification"
                    and e.get("outcome") == "success"
                    and _match(e.get("path", ""), item.get("path", ""))
                ]
                if matching_modifications:
                    latest_mod = matching_modifications[-1]
                    if parent != str(latest_mod.get("evidence_id", "") or ""):
                        return False
        return True

    def identity_valid(self) -> bool:
        """Validate Setup 4.43 evidence identity/replay invariants.

        Current evidence must have unique IDs and positive sequence ordering.
        Legacy ledgers may contain sequence-zero entries and are still accepted
        for backward compatibility; duplicate non-empty IDs are never accepted
        because they make parent references ambiguous.
        """
        seen: set[str] = set()
        last_seq = 0
        for item in self.entries:
            evidence_id = str(item.get("evidence_id", "") or "")
            if evidence_id:
                if evidence_id in seen:
                    return False
                seen.add(evidence_id)
            sequence = max(0, int(item.get("sequence", 0) or 0))
            if sequence and sequence <= last_seq:
                return False
            if sequence:
                last_seq = sequence
        return True

    def evaluate(self, verification: Any = None, verification_requested: bool = False, change_epoch: int = 0, modified_generations: Any = None) -> "CompletionEvidenceLedger":
        if not verification_requested:
            self.status = "not_required"
            self.missing_requirements = []
            return self

        current_epoch = normalize_epoch(change_epoch)
        fresh_entries = [e for e in self.entries if is_fresh(e, current_epoch)]
        if isinstance(modified_generations, dict) and modified_generations:
            modification = all(
                any(
                    e.get("category") == "modification"
                    and e.get("outcome") == "success"
                    and _match(e.get("path", ""), resource)
                    and normalize_epoch(e.get("change_epoch", 0)) >= normalize_epoch(generation)
                    for e in self.entries
                )
                for resource, generation in modified_generations.items()
                if normalize_resource_key(resource) and normalize_epoch(generation) > 0
            )
            verification_entries = [
                e for e in self.entries
                if e.get("category") == "verification" and e.get("outcome") == "success"
            ]
        else:
            modification = any(e.get("category") == "modification" and e.get("outcome") == "success" for e in fresh_entries)
            verification_entries = [e for e in fresh_entries if e.get("category") == "verification" and e.get("outcome") == "success"]
        missing: list[str] = []
        if not self.identity_valid():
            missing.append("valid evidence identity/replay state")
        if not self.integrity_valid():
            missing.append("valid evidence integrity chain")
        if self.checkpoint_hash and not self.checkpoint_valid():
            missing.append("valid evidence audit checkpoint")
        if not modification:
            missing.append("successful modification evidence")

        required_paths = list(getattr(verification, "required_paths", []) or []) if verification is not None else []
        if not self.provenance_valid(required_paths):
            missing.append("valid evidence provenance chain")
        if verification is None or getattr(verification, "status", "pending") != "complete":
            missing.append("complete change-impact verification")
        for required in required_paths:
            if isinstance(modified_generations, dict) and modified_generations:
                generation = 0
                for resource, value in modified_generations.items():
                    if _match(resource, required):
                        generation = max(generation, normalize_epoch(value))
                if generation > 0:
                    valid = any(
                        _match(e.get("path", ""), required)
                        and is_resource_fresh(e, required, modified_generations)
                        for e in verification_entries
                    )
                else:
                    valid = any(
                        _match(e.get("path", ""), required)
                        and is_fresh(e, current_epoch)
                        for e in verification_entries
                    )
            else:
                valid = any(_match(e.get("path", ""), required) for e in verification_entries)
            if not valid:
                missing.append(f"verification evidence for {required}")

        self.missing_requirements = missing[:MAX_EVIDENCE]
        self.status = "sufficient" if not self.missing_requirements else "insufficient"
        # Establish a fresh checkpoint after evaluation. If a prior checkpoint
        # was invalid, the current evaluation intentionally records the repaired
        # audit boundary; completion remains blocked only until this evaluation
        # has incorporated all current evidence.
        self.create_checkpoint()
        return self

    def summary(self) -> str:
        if self.status == "not_required":
            return "Completion evidence is not required for this task."
        if self.status == "sufficient":
            return f"Completion evidence sufficient ({len(self.entries)} recorded evidence item(s))."
        return "Completion evidence insufficient: " + ", ".join(self.missing_requirements[:8]) + "."


def make_evidence(action: str, category: str, path: str, result: Any, change_epoch: int = 0, resource_epoch: int = 0, sequence: int = 0, parent_evidence_id: str = "") -> CompletionEvidence:
    outcome = "success"
    return CompletionEvidence(
        evidence_id=_fingerprint(f"{action}|{path}|{result}")[:12],
        action=str(action),
        category=str(category),
        path=_norm(path),
        outcome=outcome,
        fingerprint=_fingerprint(result),
        change_epoch=normalize_epoch(change_epoch),
        resource_epoch=normalize_epoch(resource_epoch or change_epoch),
        sequence=max(0, int(sequence or 0)),
        parent_evidence_id=str(parent_evidence_id or ""),
    )
