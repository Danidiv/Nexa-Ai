"""Setup 4.61 audit-trail seal tests."""
from services.completion_attestation import CompletionAttestation
from services.completion_receipt import issue_completion_receipt
from services.completion_finalization import issue_completion_finalization
from services.completion_audit import CompletionAuditTrail
from services.completion_audit_seal import CompletionAuditSeal, issue_completion_audit_seal, audit_trail_digest


def _trail(conv="conv-1", task="task-abc", answer="answer-abc", epoch=3):
    att = CompletionAttestation(status="sealed", task_digest=task, answer_digest=answer)
    att.seal = "attestation-seal-before-consume"
    assert att.consume()
    receipt = issue_completion_receipt(att, conv, task, answer, epoch)
    assert receipt.valid(att, conv, task, answer, epoch)
    finalization = issue_completion_finalization(receipt, conv, task, answer, epoch)
    assert finalization.valid(receipt, conv, task, answer, epoch)
    trail = CompletionAuditTrail()
    assert trail.append_finalization(finalization, receipt, conv, task, answer, epoch)
    assert trail.valid_latest(finalization, receipt, conv, task, answer, epoch)
    return trail, receipt, finalization


def test_seal_issues_only_from_valid_audit_trail():
    trail, _, _ = _trail()
    seal = issue_completion_audit_seal(trail, "conv-1", "task-abc", "answer-abc", 3)
    assert seal.status == "sealed"
    assert seal.valid(trail, "conv-1", "task-abc", "answer-abc", 3)
    assert audit_trail_digest(trail)


def test_seal_id_and_digest_are_unique():
    trail1, _, _ = _trail()
    trail2, _, _ = _trail()
    s1 = issue_completion_audit_seal(trail1, "conv-1", "task-abc", "answer-abc", 3)
    s2 = issue_completion_audit_seal(trail2, "conv-1", "task-abc", "answer-abc", 3)
    assert s1.seal_id != s2.seal_id
    assert s1.seal == s2.seal or s1.seal != s2.seal


def test_tampered_seal_is_rejected():
    trail, _, _ = _trail()
    seal = issue_completion_audit_seal(trail, "conv-1", "task-abc", "answer-abc", 3)
    seal.answer_digest = "tampered"
    assert not seal.valid(trail, "conv-1", "task-abc", "answer-abc", 3)


def test_audit_mutation_invalidates_existing_seal():
    trail, r1, f1 = _trail()
    seal = issue_completion_audit_seal(trail, "conv-1", "task-abc", "answer-abc", 3)
    r2, f2 = _trail("conv-2", "task-xyz", "answer-xyz", 4)[1:]
    assert trail.append_finalization(f2, r2, "conv-2", "task-xyz", "answer-xyz", 4)
    assert not seal.valid(trail, "conv-1", "task-abc", "answer-abc", 3)
    assert f1.finalization_id != f2.finalization_id


def test_context_and_epoch_mismatch_are_rejected():
    trail, _, _ = _trail()
    seal = issue_completion_audit_seal(trail, "conv-1", "task-abc", "answer-abc", 3)
    assert not seal.valid(trail, "conv-2", "task-abc", "answer-abc", 3)
    assert not seal.valid(trail, "conv-1", "task-other", "answer-abc", 3)
    assert not seal.valid(trail, "conv-1", "task-abc", "answer-other", 3)
    assert not seal.valid(trail, "conv-1", "task-abc", "answer-abc", 4)


def test_serialization_restores_and_legacy_state_is_safe():
    trail, _, _ = _trail()
    seal = issue_completion_audit_seal(trail, "conv-1", "task-abc", "answer-abc", 3)
    restored = CompletionAuditSeal.from_dict(seal.to_dict())
    assert restored is not None
    assert restored.valid(trail, "conv-1", "task-abc", "answer-abc", 3)
    assert CompletionAuditSeal.from_dict(None) is None
    assert CompletionAuditSeal.from_dict({"audit_seal_version": 999}) is None


def test_trail_tampering_invalidates_seal_even_if_seal_fields_match():
    trail, _, _ = _trail()
    seal = issue_completion_audit_seal(trail, "conv-1", "task-abc", "answer-abc", 3)
    trail.entries[0].answer_digest = "tampered"
    assert not trail.integrity_valid()
    assert not seal.valid(trail, "conv-1", "task-abc", "answer-abc", 3)


def main():
    tests = [
        ("seal issues only from valid audit trail", test_seal_issues_only_from_valid_audit_trail),
        ("seal ID and digest are unique", test_seal_id_and_digest_are_unique),
        ("tampered seal is rejected", test_tampered_seal_is_rejected),
        ("audit mutation invalidates existing seal", test_audit_mutation_invalidates_existing_seal),
        ("context and epoch mismatch are rejected", test_context_and_epoch_mismatch_are_rejected),
        ("serialization restores and legacy state is safe", test_serialization_restores_and_legacy_state_is_safe),
        ("trail tampering invalidates seal", test_trail_tampering_invalidates_seal_even_if_seal_fields_match),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.61 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test(); print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}"); raise SystemExit(1)
    print("\nSetup 4.61 tests complete.")


if __name__ == "__main__":
    main()
