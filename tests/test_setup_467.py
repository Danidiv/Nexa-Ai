"""Setup 4.67 tests: append-only terminal emission audit history."""
from __future__ import annotations

import copy

from services.completion_emission_audit import (
    CompletionEmissionAuditEntry,
    CompletionEmissionAuditTrail,
)


def _fake_chain():
    class Obj:
        pass
    emission = Obj(); dispatch = Obj(); release = Obj(); commitment = Obj(); proof = Obj()
    emission.status = "emitted"; emission.emitted = True; emission.emission_id = "emission-1"; emission.seal = "emission-seal"
    dispatch.consumed = True; dispatch.dispatch_id = "dispatch-1"; dispatch.seal = "dispatch-seal"
    release.release_id = "release-1"
    commitment.commitment_id = "commit-1"
    proof.proof_id = "proof-1"
    return emission, dispatch, release, commitment, proof


def _append(trail=None):
    trail = trail or CompletionEmissionAuditTrail()
    chain = _fake_chain()
    entry = trail.append_emission(*chain, "conv", "task", "answer", 3)
    return trail, chain, entry


def test_append_only_from_emitted_dispatch():
    trail, chain, entry = _append()
    assert entry is not None and entry.sequence == 1
    assert trail.integrity_valid()


def test_binds_terminal_emission_identity():
    trail, chain, entry = _append()
    assert entry.emission_id == "emission-1"
    assert entry.dispatch_id == "dispatch-1"
    assert entry.release_id == "release-1"
    assert entry.commitment_id == "commit-1"
    assert entry.proof_id == "proof-1"
    assert entry.task_digest == "task" and entry.answer_digest == "answer"


def test_hash_chain_and_tamper_detection():
    trail, chain, first = _append()
    emission2 = copy.copy(chain[0]); emission2.emission_id = "emission-2"; emission2.seal = "emission-seal-2"
    dispatch2 = copy.copy(chain[1]); dispatch2.dispatch_id = "dispatch-2"; dispatch2.seal = "dispatch-seal-2"
    second = trail.append_emission(emission2, dispatch2, chain[2], chain[3], chain[4], "conv", "task2", "answer2", 4)
    assert second is not None and second.sequence == 2 and second.previous_hash == first.entry_hash
    assert trail.integrity_valid()
    second.answer_digest = "tampered"
    assert not trail.integrity_valid()


def test_duplicate_emission_is_rejected():
    trail, chain, entry = _append()
    assert trail.append_emission(*chain, "conv", "task", "answer", 3) is None
    assert len(trail.entries) == 1


def test_latest_identity_context_and_epoch_validation():
    trail, chain, entry = _append()
    assert trail.valid_latest(chain[0], chain[1], chain[2], chain[3], chain[4], "conv", "task", "answer", 3)
    assert not trail.valid_latest(chain[0], chain[1], chain[2], chain[3], chain[4], "other", "task", "answer", 3)
    assert not trail.valid_latest(chain[0], chain[1], chain[2], chain[3], chain[4], "conv", "other", "answer", 3)
    assert not trail.valid_latest(chain[0], chain[1], chain[2], chain[3], chain[4], "conv", "task", "answer", 4)


def test_dispatch_mutation_invalidates_latest():
    trail, chain, entry = _append()
    assert trail.valid_latest(chain[0], chain[1], chain[2], chain[3], chain[4], "conv", "task", "answer", 3)
    chain[1].seal = "changed"
    assert not trail.valid_latest(chain[0], chain[1], chain[2], chain[3], chain[4], "conv", "task", "answer", 3)


def test_serialization_and_legacy_restore():
    trail, chain, entry = _append()
    restored = CompletionEmissionAuditTrail.from_dict(trail.to_dict())
    assert restored is not None and restored.integrity_valid() and restored.latest().audit_id == entry.audit_id
    legacy = trail.to_dict(); legacy.pop("completion_emission_audit_version", None)
    for item in legacy["entries"]:
        item.pop("completion_emission_audit_entry_version", None)
    restored_legacy = CompletionEmissionAuditTrail.from_dict(legacy)
    assert restored_legacy is not None and restored_legacy.integrity_valid()


def test_bounded_rollover_preserves_integrity():
    trail = CompletionEmissionAuditTrail()
    last = None
    for i in range(35):
        emission, dispatch, release, commitment, proof = _fake_chain()
        emission.emission_id = f"emission-{i}"
        emission.seal = f"emission-seal-{i}"
        dispatch.dispatch_id = f"dispatch-{i}"
        dispatch.seal = f"dispatch-seal-{i}"
        last = trail.append_emission(emission, dispatch, release, commitment, proof, "conv", f"task-{i}", f"answer-{i}", i)
        assert last is not None
    assert len(trail.entries) == 32
    assert trail.entries[0].sequence == 4
    assert trail.entries[-1].sequence == 35
    assert trail.anchor_hash == trail.entries[0].previous_hash
    assert trail.integrity_valid()


def test_missing_upstream_cannot_append():
    trail = CompletionEmissionAuditTrail()
    emission, dispatch, release, commitment, proof = _fake_chain()
    dispatch.consumed = False
    assert trail.append_emission(emission, dispatch, release, commitment, proof, "conv", "task", "answer", 3) is None
    assert not trail.entries


def main():
    tests = [
        ("audit appends only from emitted dispatch", test_append_only_from_emitted_dispatch),
        ("audit binds terminal emission identity", test_binds_terminal_emission_identity),
        ("hash chain and tamper detection", test_hash_chain_and_tamper_detection),
        ("duplicate emission is rejected", test_duplicate_emission_is_rejected),
        ("latest identity context and epoch validation", test_latest_identity_context_and_epoch_validation),
        ("dispatch mutation invalidates latest", test_dispatch_mutation_invalidates_latest),
        ("serialization and legacy restore", test_serialization_and_legacy_restore),
        ("bounded rollover preserves integrity", test_bounded_rollover_preserves_integrity),
        ("missing upstream cannot append", test_missing_upstream_cannot_append),
    ]
    print("=" * 60); print("AZIZ AI SETUP 4.67 TEST"); print("=" * 60)
    for name, fn in tests:
        try:
            fn(); print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}"); raise
    print("\nSetup 4.67 tests complete.")

if __name__ == "__main__":
    main()
