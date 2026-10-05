"""Setup 4.69 tests: end-to-end terminal completion consistency preflight."""
from __future__ import annotations

from services.completion_terminal_consistency import (
    CompletionTerminalConsistency,
    build_terminal_consistency,
)


class Obj:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def _chain():
    conv = "conv-1"; task = "task-1"; answer = "answer-1"; epoch = 4
    receipt = Obj(status="issued", receipt_id="receipt-1", conversation_id_digest="", task_digest=task, answer_digest=answer, change_epoch=epoch,
                  valid=lambda *a, **k: True, seal="receipt-seal")
    finalization = Obj(status="finalized", finalized=True, finalization_id="final-1", conversation_id_digest="", task_digest=task, answer_digest=answer, change_epoch=epoch,
                       valid=lambda *a, **k: True, seal="final-seal")
    audit = Obj(valid_latest=lambda *a, **k: True, integrity_valid=lambda: True, latest=lambda: Obj(conversation_id_digest="", task_digest=task, answer_digest=answer, change_epoch=epoch))
    audit_seal = Obj(valid=lambda *a, **k: True)
    proof = Obj(status="sealed", sealed=True, proof_id="proof-1")
    commitment = Obj(status="committed", commitment_id="commit-1")
    release = Obj(status="released", consumed=True, release_id="release-1")
    dispatch = Obj(status="authorized", authorized=True, consumed=True, dispatch_id="dispatch-1",
                   consumed_valid=lambda *a, **k: True, seal="dispatch-seal")
    emission = Obj(status="emitted", prepared=True, emitted=True, emission_id="emission-1",
                   valid_emitted=lambda *a, **k: True, seal="emission-seal")
    emission_audit = Obj(
        valid_latest=lambda *a, **k: True,
        latest=lambda: Obj(conversation_id_digest="", task_digest=task, answer_digest=answer, change_epoch=epoch,
                           emission_id="emission-1", emission_seal_digest=""),
    )
    recovery = Obj(status="reconciled", valid=lambda: True,
                   matches_context=lambda *a, **k: True)
    return (dispatch, release, commitment, proof, Obj(consumed=True), receipt,
            finalization, audit, audit_seal, emission, emission_audit, recovery,
            conv, task, answer, epoch)


def build():
    return build_terminal_consistency(*_chain())


def test_consistent_chain_passes():
    record = build()
    assert record.status == "consistent"
    assert record.is_consistent()
    assert record.valid()


def test_consistency_is_read_only():
    chain = _chain()
    before = [dict(x.__dict__) if hasattr(x, "__dict__") else x for x in chain[:12]]
    build_terminal_consistency(*chain)
    after = [dict(x.__dict__) if hasattr(x, "__dict__") else x for x in chain[:12]]
    assert before == after


def test_dispatch_failure_blocks_consistency():
    chain = list(_chain())
    chain[0].consumed_valid = lambda *a, **k: False
    record = build_terminal_consistency(*chain)
    assert record.status == "inconsistent"
    assert "dispatch_consumed_valid" in record.failures
    assert not record.is_consistent()


def test_emission_failure_blocks_consistency():
    chain = list(_chain())
    chain[9].valid_emitted = lambda *a, **k: False
    record = build_terminal_consistency(*chain)
    assert "emission_emitted_valid" in record.failures


def test_recovery_failure_blocks_consistency():
    chain = list(_chain())
    chain[11].status = "orphaned"
    record = build_terminal_consistency(*chain)
    assert "emission_recovery_reconciled" in record.failures


def test_context_drift_is_detected():
    chain = list(_chain())
    chain[5].task_digest = "other-task"
    record = build_terminal_consistency(*chain)
    assert "task_digest_aligned" in record.failures


def test_epoch_drift_is_detected():
    chain = list(_chain())
    chain[6].change_epoch = 99
    record = build_terminal_consistency(*chain)
    assert "epoch_aligned" in record.failures


def test_tampered_consistency_seal_is_rejected():
    record = build()
    record.failures.append("tampered")
    assert not record.valid()


def test_serialization_and_legacy_restore():
    record = build()
    restored = CompletionTerminalConsistency.from_dict(record.to_dict())
    assert restored is not None and restored.valid() and restored.is_consistent()
    legacy = record.to_dict()
    legacy.pop("completion_terminal_consistency_version", None)
    restored_legacy = CompletionTerminalConsistency.from_dict(legacy)
    assert restored_legacy is not None and restored_legacy.valid()


def test_no_chain_is_inconsistent():
    record = build_terminal_consistency(*([None, None, None, None, None, None, None, None, None, None, None, None, "conv", "task", "answer", 1]))
    assert record.status == "inconsistent"
    assert record.valid()


def main():
    tests = [
        ("consistent chain passes", test_consistent_chain_passes),
        ("consistency is read-only", test_consistency_is_read_only),
        ("dispatch failure blocks consistency", test_dispatch_failure_blocks_consistency),
        ("emission failure blocks consistency", test_emission_failure_blocks_consistency),
        ("recovery failure blocks consistency", test_recovery_failure_blocks_consistency),
        ("context drift is detected", test_context_drift_is_detected),
        ("epoch drift is detected", test_epoch_drift_is_detected),
        ("tampered consistency seal is rejected", test_tampered_consistency_seal_is_rejected),
        ("serialization and legacy restore", test_serialization_and_legacy_restore),
        ("no chain is inconsistent", test_no_chain_is_inconsistent),
    ]
    print("=" * 60); print("AZIZ AI SETUP 4.69 TEST"); print("=" * 60)
    for name, fn in tests:
        fn(); print(f"[PASS] {name}")
    print("\nSetup 4.69 tests complete.")


if __name__ == "__main__":
    main()
