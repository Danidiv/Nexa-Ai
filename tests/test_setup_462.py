"""Setup 4.62 end-to-end completion proof tests."""
from services.completion_attestation import CompletionAttestation
from services.completion_receipt import issue_completion_receipt
from services.completion_finalization import issue_completion_finalization
from services.completion_audit import CompletionAuditTrail
from services.completion_audit_seal import issue_completion_audit_seal
from services.completion_proof import CompletionProof, issue_completion_proof


def _bundle(conv="conv-1", task="task-abc", answer="answer-abc", epoch=3):
    att = CompletionAttestation(status="sealed", task_digest=task, answer_digest=answer)
    att.seal = "attestation-seal"
    assert att.consume()
    receipt = issue_completion_receipt(att, conv, task, answer, epoch)
    assert receipt.valid(att, conv, task, answer, epoch)
    finalization = issue_completion_finalization(receipt, conv, task, answer, epoch)
    assert finalization.valid(receipt, conv, task, answer, epoch)
    trail = CompletionAuditTrail()
    assert trail.append_finalization(finalization, receipt, conv, task, answer, epoch)
    audit_seal = issue_completion_audit_seal(trail, conv, task, answer, epoch)
    assert audit_seal.valid(trail, conv, task, answer, epoch)
    return att, receipt, finalization, trail, audit_seal


def test_proof_issues_only_from_complete_valid_chain():
    bundle = _bundle()
    proof = issue_completion_proof(*bundle, "conv-1", "task-abc", "answer-abc", 3)
    assert proof.status == "sealed"
    assert proof.valid(*bundle, "conv-1", "task-abc", "answer-abc", 3)


def test_proof_binds_every_completion_stage():
    bundle = _bundle()
    proof = issue_completion_proof(*bundle, "conv-1", "task-abc", "answer-abc", 3)
    assert proof.attestation_seal_digest
    assert proof.receipt_id and proof.receipt_seal_digest
    assert proof.finalization_id and proof.finalization_seal_digest
    assert proof.audit_id and proof.audit_entry_hash
    assert proof.audit_seal_id and proof.audit_seal_digest


def test_tampered_proof_is_rejected():
    bundle = _bundle()
    proof = issue_completion_proof(*bundle, "conv-1", "task-abc", "answer-abc", 3)
    proof.answer_digest = "tampered"
    assert not proof.valid(*bundle, "conv-1", "task-abc", "answer-abc", 3)


def test_upstream_mutation_invalidates_proof():
    bundle = _bundle()
    proof = issue_completion_proof(*bundle, "conv-1", "task-abc", "answer-abc", 3)
    bundle[3].entries[0].answer_digest = "tampered"
    assert not proof.valid(*bundle, "conv-1", "task-abc", "answer-abc", 3)


def test_context_and_epoch_mismatch_are_rejected():
    bundle = _bundle()
    proof = issue_completion_proof(*bundle, "conv-1", "task-abc", "answer-abc", 3)
    assert not proof.valid(*bundle, "conv-2", "task-abc", "answer-abc", 3)
    assert not proof.valid(*bundle, "conv-1", "task-other", "answer-abc", 3)
    assert not proof.valid(*bundle, "conv-1", "task-abc", "answer-other", 3)
    assert not proof.valid(*bundle, "conv-1", "task-abc", "answer-abc", 4)


def test_serialization_restores_and_legacy_state_is_safe():
    bundle = _bundle()
    proof = issue_completion_proof(*bundle, "conv-1", "task-abc", "answer-abc", 3)
    restored = CompletionProof.from_dict(proof.to_dict())
    assert restored is not None
    assert restored.valid(*bundle, "conv-1", "task-abc", "answer-abc", 3)
    assert CompletionProof.from_dict(None) is None
    assert CompletionProof.from_dict({"completion_proof_version": 999}) is None


def test_missing_upstream_stage_cannot_create_proof():
    bundle = _bundle()
    assert issue_completion_proof(CompletionAttestation(), *bundle[1:], "conv-1", "task-abc", "answer-abc", 3).status == "not_required"


def test_audit_seal_tampering_invalidates_proof():
    bundle = _bundle()
    proof = issue_completion_proof(*bundle, "conv-1", "task-abc", "answer-abc", 3)
    bundle[4].answer_digest = "tampered"
    assert not proof.valid(*bundle, "conv-1", "task-abc", "answer-abc", 3)


def main():
    tests = [
        ("proof issues only from complete valid chain", test_proof_issues_only_from_complete_valid_chain),
        ("proof binds every completion stage", test_proof_binds_every_completion_stage),
        ("tampered proof is rejected", test_tampered_proof_is_rejected),
        ("upstream mutation invalidates proof", test_upstream_mutation_invalidates_proof),
        ("context and epoch mismatch are rejected", test_context_and_epoch_mismatch_are_rejected),
        ("serialization restores and legacy state is safe", test_serialization_restores_and_legacy_state_is_safe),
        ("missing upstream stage cannot create proof", test_missing_upstream_stage_cannot_create_proof),
        ("audit seal tampering invalidates proof", test_audit_seal_tampering_invalidates_proof),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.62 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test(); print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}"); raise SystemExit(1)
    print("\nSetup 4.62 tests complete.")


if __name__ == "__main__":
    main()
