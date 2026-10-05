"""Setup 4.68 tests: crash-safe terminal emission reconciliation."""
from __future__ import annotations

import copy

from services.completion_emission import issue_completion_emission
from services.completion_emission_audit import CompletionEmissionAuditTrail
from services.completion_emission_recovery import (
    CompletionEmissionRecovery,
    inspect_completion_emission,
    reconcile_emitted,
)


def _chain():
    class Obj:
        pass
    emission = Obj(); dispatch = Obj(); release = Obj(); commitment = Obj(); proof = Obj()
    dispatch.consumed = True; dispatch.dispatch_id = "dispatch-1"; dispatch.seal = "dispatch-seal"
    release.release_id = "release-1"
    commitment.commitment_id = "commit-1"
    proof.proof_id = "proof-1"
    # Use the real issuer so its seal semantics are covered by recovery tests.
    dispatch.status = "authorized"
    emission.status = "emitted"; emission.prepared = True; emission.emitted = True
    emission.emission_id = "emission-1"; emission.seal = "emission-seal"
    return emission, dispatch, release, commitment, proof


def _audit():
    emission, dispatch, release, commitment, proof = _chain()
    trail = CompletionEmissionAuditTrail()
    entry = trail.append_emission(emission, dispatch, release, commitment, proof, "conv", "task", "answer", 3)
    return emission, dispatch, release, commitment, proof, trail, entry


def test_prepared_emission_is_detected_as_pending():
    emission, *_ = _chain()
    emission.status = "prepared"; emission.emitted = False; emission.prepared = True
    recovery = inspect_completion_emission(emission, None, "conv", "task", "answer", 3)
    assert recovery.status == "pending" and recovery.blocks_terminal_emit()
    assert recovery.valid()


def test_emitted_emission_reconciles_with_audit():
    emission, dispatch, release, commitment, proof, trail, entry = _audit()
    recovery = reconcile_emitted(emission, entry, trail, "conv", "task", "answer", 3)
    assert recovery.status == "reconciled" and recovery.resolved
    assert recovery.audit_id == entry.audit_id
    assert recovery.valid()


def test_missing_audit_is_orphaned():
    emission, *_ = _chain()
    trail = CompletionEmissionAuditTrail()
    recovery = reconcile_emitted(emission, None, trail, "conv", "task", "answer", 3)
    assert recovery.status == "orphaned" and recovery.resolved
    assert recovery.valid()


def test_tampered_recovery_is_rejected():
    emission, dispatch, release, commitment, proof, trail, entry = _audit()
    recovery = reconcile_emitted(emission, entry, trail, "conv", "task", "answer", 3)
    recovery.answer_digest = "tampered"
    assert not recovery.valid()


def test_context_mismatch_is_detected():
    emission, dispatch, release, commitment, proof, trail, entry = _audit()
    recovery = reconcile_emitted(emission, entry, trail, "conv", "task", "answer", 3)
    assert recovery.matches_context("conv", "task", "answer", 3)
    assert not recovery.matches_context("other", "task", "answer", 3)
    assert not recovery.matches_context("conv", "other", "answer", 3)
    assert not recovery.matches_context("conv", "task", "answer", 4)


def test_audit_mutation_invalidates_reconciliation():
    emission, dispatch, release, commitment, proof, trail, entry = _audit()
    recovery = reconcile_emitted(emission, entry, trail, "conv", "task", "answer", 3)
    assert recovery.valid()
    entry.entry_hash = "tampered"
    assert not trail.integrity_valid()
    broken = reconcile_emitted(emission, entry, trail, "conv", "task", "answer", 3)
    assert broken.status == "orphaned"


def test_serialization_and_legacy_restore():
    emission, dispatch, release, commitment, proof, trail, entry = _audit()
    recovery = reconcile_emitted(emission, entry, trail, "conv", "task", "answer", 3)
    restored = CompletionEmissionRecovery.from_dict(recovery.to_dict())
    assert restored is not None and restored.valid()
    legacy = recovery.to_dict(); legacy.pop("completion_emission_recovery_version", None)
    restored_legacy = CompletionEmissionRecovery.from_dict(legacy)
    assert restored_legacy is not None and restored_legacy.valid()


def test_recovery_does_not_store_raw_output():
    emission, dispatch, release, commitment, proof, trail, entry = _audit()
    recovery = reconcile_emitted(emission, entry, trail, "conv", "task", "answer", 3)
    raw = recovery.to_dict()
    encoded = str(raw)
    assert "answer text" not in encoded
    assert "tool output" not in encoded
    assert "answer_digest" in raw


def test_no_emission_is_not_required():
    recovery = inspect_completion_emission(None, None, "conv", "task", "answer", 3)
    assert recovery.status == "not_required"
    assert recovery.valid()


def main():
    tests = [
        ("prepared emission is detected as pending", test_prepared_emission_is_detected_as_pending),
        ("emitted emission reconciles with audit", test_emitted_emission_reconciles_with_audit),
        ("missing audit is orphaned", test_missing_audit_is_orphaned),
        ("tampered recovery is rejected", test_tampered_recovery_is_rejected),
        ("context mismatch is detected", test_context_mismatch_is_detected),
        ("audit mutation invalidates reconciliation", test_audit_mutation_invalidates_reconciliation),
        ("serialization and legacy restore", test_serialization_and_legacy_restore),
        ("recovery does not store raw output", test_recovery_does_not_store_raw_output),
        ("no emission is not required", test_no_emission_is_not_required),
    ]
    print("=" * 60); print("AZIZ AI SETUP 4.68 TEST"); print("=" * 60)
    for name, fn in tests:
        try:
            fn(); print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}"); raise
    print("\nSetup 4.68 tests complete.")

if __name__ == "__main__":
    main()
