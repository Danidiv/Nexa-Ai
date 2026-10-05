"""Setup 4.60 persistent completion audit-trail tests."""
from services.completion_attestation import CompletionAttestation
from services.completion_receipt import issue_completion_receipt
from services.completion_finalization import issue_completion_finalization
from services.completion_audit import CompletionAuditTrail, MAX_ENTRIES


def _finalized(conv="conv-1", task="task-abc", answer="answer-abc", epoch=3):
    att = CompletionAttestation(status="sealed", task_digest=task, answer_digest=answer)
    att.seal = "attestation-seal-before-consume"
    assert att.consume()
    receipt = issue_completion_receipt(att, conv, task, answer, epoch)
    assert receipt.valid(att, conv, task, answer, epoch)
    finalization = issue_completion_finalization(receipt, conv, task, answer, epoch)
    assert finalization.valid(receipt, conv, task, answer, epoch)
    return receipt, finalization


def test_audit_appends_valid_finalization():
    receipt, finalization = _finalized()
    trail = CompletionAuditTrail()
    entry = trail.append_finalization(finalization, receipt, "conv-1", "task-abc", "answer-abc", 3)
    assert entry is not None
    assert trail.integrity_valid()
    assert trail.valid_latest(finalization, receipt, "conv-1", "task-abc", "answer-abc", 3)


def test_audit_id_and_hash_chain_are_unique():
    r1, f1 = _finalized()
    r2, f2 = _finalized()
    trail = CompletionAuditTrail()
    e1 = trail.append_finalization(f1, r1, "conv-1", "task-abc", "answer-abc", 3)
    e2 = trail.append_finalization(f2, r2, "conv-1", "task-abc", "answer-abc", 3)
    assert e1 and e2
    assert e1.audit_id != e2.audit_id
    assert e1.entry_hash != e2.entry_hash
    assert e2.previous_hash == e1.entry_hash
    assert trail.integrity_valid()


def test_tampered_audit_entry_is_rejected():
    receipt, finalization = _finalized()
    trail = CompletionAuditTrail()
    trail.append_finalization(finalization, receipt, "conv-1", "task-abc", "answer-abc", 3)
    trail.entries[0].answer_digest = "tampered"
    assert not trail.integrity_valid()
    assert not trail.valid_latest(finalization, receipt, "conv-1", "task-abc", "answer-abc", 3)


def test_audit_rejects_duplicate_finalization_and_mismatched_context():
    receipt, finalization = _finalized()
    trail = CompletionAuditTrail()
    assert trail.append_finalization(finalization, receipt, "conv-1", "task-abc", "answer-abc", 3)
    assert trail.append_finalization(finalization, receipt, "conv-1", "task-abc", "answer-abc", 3) is None
    assert not trail.valid_latest(finalization, receipt, "conv-2", "task-abc", "answer-abc", 3)
    assert not trail.valid_latest(finalization, receipt, "conv-1", "task-other", "answer-abc", 3)


def test_audit_serialization_restores_and_validates():
    receipt, finalization = _finalized()
    trail = CompletionAuditTrail()
    trail.append_finalization(finalization, receipt, "conv-1", "task-abc", "answer-abc", 3)
    restored = CompletionAuditTrail.from_dict(trail.to_dict())
    assert restored is not None
    assert restored.integrity_valid()
    assert restored.valid_latest(finalization, receipt, "conv-1", "task-abc", "answer-abc", 3)


def test_bounded_rollover_preserves_integrity():
    trail = CompletionAuditTrail()
    records = []
    for i in range(MAX_ENTRIES + 3):
        conv = f"conv-{i}"
        task = f"task-{i}"
        answer = f"answer-{i}"
        receipt, finalization = _finalized(conv, task, answer, i)
        entry = trail.append_finalization(finalization, receipt, conv, task, answer, i)
        assert entry is not None
        records.append((receipt, finalization, conv, task, answer, i))
        assert trail.integrity_valid()
    assert len(trail.entries) == MAX_ENTRIES
    assert trail.anchor_hash
    assert trail.latest().finalization_id == records[-1][1].finalization_id
    receipt, finalization, conv, task, answer, epoch = records[-1]
    assert trail.valid_latest(finalization, receipt, conv, task, answer, epoch)


def test_legacy_459_state_without_audit_trail_is_safe():
    assert CompletionAuditTrail.from_dict(None) is None
    empty = CompletionAuditTrail()
    assert empty.entries == []
    assert empty.integrity_valid()


def main():
    tests = [
        ("audit appends valid finalization", test_audit_appends_valid_finalization),
        ("audit ID and hash chain are unique", test_audit_id_and_hash_chain_are_unique),
        ("tampered audit entry is rejected", test_tampered_audit_entry_is_rejected),
        ("audit rejects duplicate finalization and mismatched context", test_audit_rejects_duplicate_finalization_and_mismatched_context),
        ("audit serialization restores and validates", test_audit_serialization_restores_and_validates),
        ("bounded rollover preserves integrity", test_bounded_rollover_preserves_integrity),
        ("legacy Setup 4.59 state without audit trail is safe", test_legacy_459_state_without_audit_trail_is_safe),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.60 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test(); print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}"); raise SystemExit(1)
    print("\nSetup 4.60 tests complete.")


if __name__ == "__main__":
    main()
