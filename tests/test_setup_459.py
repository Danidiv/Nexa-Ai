"""Setup 4.59 finalization-lock tests."""
from services.completion_receipt import issue_completion_receipt
from services.completion_attestation import CompletionAttestation
from services.completion_finalization import CompletionFinalization, issue_completion_finalization


def _receipt():
    att = CompletionAttestation(status="sealed", task_digest="task-abc", answer_digest="answer-abc")
    att.seal = "attestation-seal-before-consume"
    assert att.consume()
    receipt = issue_completion_receipt(att, "conv-1", "task-abc", "answer-abc", 3)
    assert receipt.valid(att, "conv-1", "task-abc", "answer-abc", 3)
    return receipt


def test_finalization_issues_only_from_valid_receipt():
    receipt = _receipt()
    record = issue_completion_finalization(receipt, "conv-1", "task-abc", "answer-abc", 3)
    assert record.status == "finalized"
    assert record.finalized
    assert record.finalization_id
    assert record.valid(receipt, "conv-1", "task-abc", "answer-abc", 3)


def test_finalization_id_is_unique():
    r1 = _receipt(); r2 = _receipt()
    f1 = issue_completion_finalization(r1, "conv-1", "task-abc", "answer-abc", 3)
    f2 = issue_completion_finalization(r2, "conv-1", "task-abc", "answer-abc", 3)
    assert f1.finalization_id != f2.finalization_id


def test_tampered_finalization_is_rejected():
    receipt = _receipt()
    record = issue_completion_finalization(receipt, "conv-1", "task-abc", "answer-abc", 3)
    record.answer_digest = "tampered"
    assert not record.valid(receipt, "conv-1", "task-abc", "answer-abc", 3)


def test_different_receipt_task_or_conversation_is_rejected():
    receipt = _receipt()
    record = issue_completion_finalization(receipt, "conv-1", "task-abc", "answer-abc", 3)
    other_receipt = _receipt()
    assert not record.valid(other_receipt, "conv-1", "task-abc", "answer-abc", 3)
    assert not record.valid(receipt, "conv-2", "task-abc", "answer-abc", 3)
    assert not record.valid(receipt, "conv-1", "task-other", "answer-abc", 3)


def test_finalization_serialization_restores_and_validates():
    receipt = _receipt()
    record = issue_completion_finalization(receipt, "conv-1", "task-abc", "answer-abc", 3)
    restored = CompletionFinalization.from_dict(record.to_dict())
    assert restored is not None
    assert restored.finalization_id == record.finalization_id
    assert restored.valid(receipt, "conv-1", "task-abc", "answer-abc", 3)


def test_legacy_setup_458_state_without_finalization_is_safe():
    assert CompletionFinalization.from_dict(None) is None
    empty = CompletionFinalization()
    assert empty.status == "not_required"
    assert not empty.finalized


def main():
    tests = [
        ("finalization issues only from valid receipt", test_finalization_issues_only_from_valid_receipt),
        ("finalization ID is unique", test_finalization_id_is_unique),
        ("tampered finalization is rejected", test_tampered_finalization_is_rejected),
        ("different receipt/task/conversation is rejected", test_different_receipt_task_or_conversation_is_rejected),
        ("finalization serialization restores and validates", test_finalization_serialization_restores_and_validates),
        ("legacy Setup 4.58 state without finalization is safe", test_legacy_setup_458_state_without_finalization_is_safe),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.59 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test(); print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}"); raise SystemExit(1)
    print("\nSetup 4.59 tests complete.")

if __name__ == "__main__":
    main()
