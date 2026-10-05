"""Setup 4.66 tests: durable two-phase terminal answer emission journal."""
from __future__ import annotations

import copy
import sys

from services.completion_emission import CompletionEmission, issue_completion_emission


def _fake_chain():
    class Obj:
        pass
    dispatch = Obj(); release = Obj(); commitment = Obj(); proof = Obj()
    attestation = Obj(); receipt = Obj(); finalization = Obj(); audit = Obj(); audit_seal = Obj()
    dispatch.status = "authorized"; dispatch.consumed = True; dispatch.dispatch_id = "dispatch-1"; dispatch.seal = "dispatch-seal"
    release.consumed = True; release.release_id = "release-1"
    commitment.status = "committed"; commitment.commitment_id = "commit-1"
    proof.status = "sealed"; proof.proof_id = "proof-1"
    return dispatch, release, commitment, proof, attestation, receipt, finalization, audit, audit_seal


def _patch_valid(dispatch):
    dispatch.consumed_valid = lambda *args: True


def test_issue_only_from_consumed_dispatch():
    chain = _fake_chain(); _patch_valid(chain[0])
    r = issue_completion_emission(chain[0], chain[1], chain[2], chain[3], "conv", "task", "answer", 3)
    assert r.status == "prepared" and r.prepared and not r.emitted


def test_binds_terminal_identity():
    chain = _fake_chain(); _patch_valid(chain[0])
    r = issue_completion_emission(*chain[:4], "conv", "task", "answer", 3)
    assert r.dispatch_id == "dispatch-1" and r.release_id == "release-1" and r.commitment_id == "commit-1" and r.proof_id == "proof-1"


def test_tampered_prepared_rejected():
    chain = _fake_chain(); _patch_valid(chain[0])
    r = issue_completion_emission(*chain[:4], "conv", "task", "answer", 3)
    r.answer_digest = "tampered"
    assert not r.valid_prepared(*chain, "conv", "task", "answer", 3)


def test_dispatch_mutation_invalidates():
    chain = _fake_chain(); _patch_valid(chain[0])
    r = issue_completion_emission(*chain[:4], "conv", "task", "answer", 3)
    assert r.valid_prepared(*chain, "conv", "task", "answer", 3)
    chain[0].seal = "changed"
    assert not r.valid_prepared(*chain, "conv", "task", "answer", 3)


def test_consume_transition_is_one_way_and_sealed():
    chain = _fake_chain(); _patch_valid(chain[0])
    r = issue_completion_emission(*chain[:4], "conv", "task", "answer", 3)
    old = r.seal
    assert r.mark_emitted()
    assert r.emitted and r.status == "emitted" and r.seal != old
    assert not r.mark_emitted()
    assert r.valid_emitted(*chain, "conv", "task", "answer", 3)


def test_context_and_epoch_mismatch_rejected():
    chain = _fake_chain(); _patch_valid(chain[0])
    r = issue_completion_emission(*chain[:4], "conv", "task", "answer", 3)
    assert not r.valid_prepared(*chain, "other", "task", "answer", 3)
    assert not r.valid_prepared(*chain, "conv", "other", "answer", 3)
    assert not r.valid_prepared(*chain, "conv", "task", "answer", 4)


def test_serialization_and_legacy_safe():
    chain = _fake_chain(); _patch_valid(chain[0])
    r = issue_completion_emission(*chain[:4], "conv", "task", "answer", 3)
    restored = CompletionEmission.from_dict(r.to_dict())
    assert restored is not None and restored.valid_prepared(*chain, "conv", "task", "answer", 3)
    legacy = r.to_dict(); legacy.pop("completion_emission_version", None)
    legacy.pop("emitted", None)
    restored_legacy = CompletionEmission.from_dict(legacy)
    assert restored_legacy is not None and not restored_legacy.emitted


def test_missing_upstream_cannot_issue():
    chain = _fake_chain(); _patch_valid(chain[0])
    broken = issue_completion_emission(None, chain[1], chain[2], chain[3], "conv", "task", "answer", 3)
    assert broken.status == "not_required"


def main():
    tests = [
        ("emission issues only from consumed dispatch", test_issue_only_from_consumed_dispatch),
        ("emission binds terminal identity", test_binds_terminal_identity),
        ("tampered prepared emission is rejected", test_tampered_prepared_rejected),
        ("dispatch mutation invalidates emission", test_dispatch_mutation_invalidates),
        ("emission transition is one-way and sealed", test_consume_transition_is_one_way_and_sealed),
        ("context and epoch mismatch are rejected", test_context_and_epoch_mismatch_rejected),
        ("serialization and legacy state are safe", test_serialization_and_legacy_safe),
        ("missing upstream cannot create emission", test_missing_upstream_cannot_issue),
    ]
    print("=" * 60); print("AZIZ AI SETUP 4.66 TEST"); print("=" * 60)
    for name, fn in tests:
        try:
            fn(); print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}"); raise
    print("\nSetup 4.66 tests complete.")

if __name__ == "__main__":
    main()
