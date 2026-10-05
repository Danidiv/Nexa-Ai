"""Setup 4.58 completion receipt tests."""
from services.completion_receipt import CompletionReceipt, issue_completion_receipt, conversation_identity_digest
from services.completion_attestation import CompletionAttestation


def _attestation():
    att = CompletionAttestation(status="sealed", task_digest="task-abc", answer_digest="answer-abc")
    att.seal = "attestation-seal-before-consume"
    assert att.consume()
    return att


def test_receipt_issues_only_from_consumed_attestation():
    att = _attestation()
    receipt = issue_completion_receipt(att, "conv-1", "task-abc", "answer-abc", 3)
    assert receipt.status == "issued"
    assert receipt.receipt_id
    assert receipt.valid(att, "conv-1", "task-abc", "answer-abc", 3)


def test_receipt_id_is_unique():
    att1 = _attestation(); att2 = _attestation()
    r1 = issue_completion_receipt(att1, "conv-1", "task-abc", "answer-abc", 3)
    r2 = issue_completion_receipt(att2, "conv-1", "task-abc", "answer-abc", 3)
    assert r1.receipt_id != r2.receipt_id


def test_tampered_receipt_is_rejected():
    att = _attestation()
    receipt = issue_completion_receipt(att, "conv-1", "task-abc", "answer-abc", 3)
    receipt.answer_digest = "tampered"
    assert not receipt.valid(att, "conv-1", "task-abc", "answer-abc", 3)


def test_different_task_or_conversation_is_rejected():
    att = _attestation()
    receipt = issue_completion_receipt(att, "conv-1", "task-abc", "answer-abc", 3)
    assert not receipt.valid(att, "conv-2", "task-abc", "answer-abc", 3)
    assert not receipt.valid(att, "conv-1", "task-other", "answer-abc", 3)


def test_receipt_serialization_restores_and_validates():
    att = _attestation()
    receipt = issue_completion_receipt(att, "conv-1", "task-abc", "answer-abc", 3)
    restored = CompletionReceipt.from_dict(receipt.to_dict())
    assert restored is not None
    assert restored.receipt_id == receipt.receipt_id
    assert restored.valid(att, "conv-1", "task-abc", "answer-abc", 3)


def test_legacy_setup_457_state_without_receipt_is_safe():
    restored = CompletionReceipt.from_dict(None)
    assert restored is None
    empty = CompletionReceipt()
    assert empty.status == "not_required"
    assert conversation_identity_digest("conv-1")


def main():
    tests = [
        ("receipt issues only from consumed attestation", test_receipt_issues_only_from_consumed_attestation),
        ("receipt ID is unique", test_receipt_id_is_unique),
        ("tampered receipt is rejected", test_tampered_receipt_is_rejected),
        ("different task or conversation is rejected", test_different_task_or_conversation_is_rejected),
        ("receipt serialization restores and validates", test_receipt_serialization_restores_and_validates),
        ("legacy Setup 4.57 state without receipt is safe", test_legacy_setup_457_state_without_receipt_is_safe),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.58 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test(); print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}"); raise SystemExit(1)
    print("\nSetup 4.58 tests complete.")

if __name__ == "__main__": main()
