"""Setup 4.69: end-to-end terminal completion consistency preflight.

This module is a read-only consistency boundary. It does not authorize, consume,
release, emit, or mutate any completion token. It verifies that all existing
terminal layers describe the same conversation/task/answer/epoch before the
final answer boundary is allowed to proceed.
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


def _seal_payload(record: "CompletionTerminalConsistency") -> dict[str, Any]:
    return {
        "version": VERSION,
        "status": record.status,
        "consistency_id": record.consistency_id,
        "conversation_id_digest": record.conversation_id_digest,
        "task_digest": record.task_digest,
        "answer_digest": record.answer_digest,
        "change_epoch": max(0, int(record.change_epoch or 0)),
        "checks": list(record.checks),
        "failures": list(record.failures),
    }


def _seal(record: "CompletionTerminalConsistency") -> str:
    encoded = json.dumps(_seal_payload(record), sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


@dataclass
class CompletionTerminalConsistency:
    """Read-only proof that the existing terminal chain is internally coherent."""

    status: str = "not_required"
    consistency_id: str = ""
    conversation_id_digest: str = ""
    task_digest: str = ""
    answer_digest: str = ""
    change_epoch: int = 0
    checks: list[str] | None = None
    failures: list[str] | None = None
    seal: str = ""

    def __post_init__(self) -> None:
        if self.checks is None:
            self.checks = []
        if self.failures is None:
            self.failures = []

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["completion_terminal_consistency_version"] = VERSION
        data["change_epoch"] = max(0, int(self.change_epoch or 0))
        data["checks"] = list(self.checks or [])
        data["failures"] = list(self.failures or [])
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionTerminalConsistency | None":
        if not isinstance(data, dict):
            return None
        if data.get("completion_terminal_consistency_version", VERSION) != VERSION:
            return None
        try:
            return cls(
                status=_norm(data.get("status")) or "not_required",
                consistency_id=_norm(data.get("consistency_id")),
                conversation_id_digest=_norm(data.get("conversation_id_digest")),
                task_digest=_norm(data.get("task_digest")),
                answer_digest=_norm(data.get("answer_digest")),
                change_epoch=max(0, int(data.get("change_epoch", 0) or 0)),
                checks=[_norm(x) for x in data.get("checks", []) if _norm(x)],
                failures=[_norm(x) for x in data.get("failures", []) if _norm(x)],
                seal=_norm(data.get("seal")),
            )
        except (TypeError, ValueError):
            return None

    def valid(self) -> bool:
        if self.status == "not_required":
            return not self.consistency_id and not self.seal
        if self.status not in {"consistent", "inconsistent"}:
            return False
        if not self.consistency_id or not self.seal:
            return False
        return _seal(self) == self.seal

    def is_consistent(self) -> bool:
        return self.status == "consistent" and self.valid() and not self.failures


def _same(value: Any, expected: str) -> bool:
    return _norm(value) == _norm(expected)


def build_terminal_consistency(
    dispatch: Any,
    release: Any,
    commitment: Any,
    proof: Any,
    attestation: Any,
    receipt: Any,
    finalization: Any,
    audit_trail: Any,
    audit_seal: Any,
    emission: Any,
    emission_audit: Any,
    emission_recovery: Any,
    conversation_id: Any,
    task_digest: str,
    answer_digest: str,
    change_epoch: int,
) -> CompletionTerminalConsistency:
    """Perform a read-only end-to-end consistency check across terminal layers."""
    task = _norm(task_digest)
    answer = _norm(answer_digest)
    epoch = max(0, int(change_epoch or 0))
    checks: list[str] = []
    failures: list[str] = []
    conv_digest = _digest(conversation_id)

    def check(name: str, ok: bool) -> None:
        (checks if ok else failures).append(name)

    dispatch_ok = bool(dispatch is not None and getattr(dispatch, "consumed_valid", lambda *a, **k: False)(
        release, commitment, proof, attestation, receipt, finalization,
        audit_trail, audit_seal, conversation_id, task, answer, epoch,
    ))
    check("dispatch_consumed_valid", dispatch_ok)
    check("release_consumed", bool(release is not None and getattr(release, "consumed", False)))
    check("commitment_committed", bool(commitment is not None and getattr(commitment, "status", "") == "committed"))
    check("proof_sealed", bool(proof is not None and getattr(proof, "status", "") == "sealed"))
    check("attestation_consumed", bool(attestation is not None and getattr(attestation, "consumed", False)))
    check("receipt_valid", bool(receipt is not None and getattr(receipt, "valid", lambda *a, **k: False)(
        attestation, conversation_id, task, answer, epoch,
    )))
    check("finalization_valid", bool(finalization is not None and getattr(finalization, "valid", lambda *a, **k: False)(
        receipt, conversation_id, task, answer, epoch,
    )))
    check("audit_latest_valid", bool(audit_trail is not None and getattr(audit_trail, "valid_latest", lambda *a, **k: False)(
        finalization, receipt, conversation_id, task, answer, epoch,
    )))
    check("audit_seal_valid", bool(audit_seal is not None and getattr(audit_seal, "valid", lambda *a, **k: False)(
        audit_trail, conversation_id, task, answer, epoch,
    )))
    check("emission_emitted_valid", bool(emission is not None and getattr(emission, "valid_emitted", lambda *a, **k: False)(
        dispatch, release, commitment, proof, attestation, receipt, finalization,
        audit_trail, audit_seal, conversation_id, task, answer, epoch,
    )))
    check("emission_audit_latest_valid", bool(emission_audit is not None and getattr(emission_audit, "valid_latest", lambda *a, **k: False)(
        emission, dispatch, release, commitment, proof, conversation_id, task, answer, epoch,
    )))
    check("emission_recovery_reconciled", bool(
        emission_recovery is not None
        and getattr(emission_recovery, "valid", lambda: False)()
        and getattr(emission_recovery, "status", "") == "reconciled"
        and getattr(emission_recovery, "matches_context", lambda *a: False)(conversation_id, task, answer, epoch)
    ))

    # Cross-layer identity checks are intentionally explicit so a valid-looking
    # individual record cannot hide a disagreement elsewhere in the chain.
    latest_emission_audit = getattr(emission_audit, "latest", lambda: None)()
    check("conversation_digest_aligned", all(
        _same(getattr(obj, "conversation_id_digest", ""), conv_digest)
        for obj in (receipt, finalization, emission, emission_recovery, latest_emission_audit)
        if obj is not None and getattr(obj, "conversation_id_digest", "")
    ))
    check("task_digest_aligned", all(
        _same(getattr(obj, "task_digest", ""), task)
        for obj in (receipt, finalization, emission, emission_recovery, latest_emission_audit)
        if obj is not None and getattr(obj, "task_digest", "")
    ))
    check("answer_digest_aligned", all(
        _same(getattr(obj, "answer_digest", ""), answer)
        for obj in (receipt, finalization, emission, emission_recovery, latest_emission_audit)
        if obj is not None and getattr(obj, "answer_digest", "")
    ))
    check("epoch_aligned", all(
        max(0, int(getattr(obj, "change_epoch", 0) or 0)) == epoch
        for obj in (receipt, finalization, emission, emission_recovery, latest_emission_audit)
        if obj is not None and hasattr(obj, "change_epoch")
    ))

    status = "consistent" if not failures else "inconsistent"
    seed = "|".join([conv_digest, task, answer, str(epoch), ",".join(checks), ",".join(failures)])
    record = CompletionTerminalConsistency(
        status=status,
        consistency_id=sha256(seed.encode("utf-8", errors="replace")).hexdigest()[:24],
        conversation_id_digest=conv_digest,
        task_digest=task,
        answer_digest=answer,
        change_epoch=epoch,
        checks=checks,
        failures=failures,
    )
    record.seal = _seal(record)
    return record
