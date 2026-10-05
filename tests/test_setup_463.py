"""Setup 4.63 terminal completion-proof commitment tests."""
from services.completion_attestation import CompletionAttestation
from services.completion_receipt import issue_completion_receipt
from services.completion_finalization import issue_completion_finalization
from services.completion_audit import CompletionAuditTrail
from services.completion_audit_seal import issue_completion_audit_seal
from services.completion_proof import issue_completion_proof
from services.completion_proof_commitment import CompletionProofCommitment, issue_completion_proof_commitment


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
    proof = issue_completion_proof(att, receipt, finalization, trail, audit_seal, conv, task, answer, epoch)
    assert proof.status == "sealed"
    assert proof.valid(att, receipt, finalization, trail, audit_seal, conv, task, answer, epoch)
    return att, receipt, finalization, trail, audit_seal, proof


def test_commitment_issues_only_from_valid_proof_chain():
    att, receipt, finalization, trail, audit_seal, proof = _bundle()
    commitment = issue_completion_proof_commitment(proof, audit_seal, finalization, receipt, "conv-1", "task-abc", "answer-abc", 3)
    assert commitment.status == "committed"
    assert commitment.committed
    assert commitment.valid(proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)


def test_commitment_binds_terminal_identities():
    att, receipt, finalization, trail, audit_seal, proof = _bundle()
    commitment = issue_completion_proof_commitment(proof, audit_seal, finalization, receipt, "conv-1", "task-abc", "answer-abc", 3)
    assert commitment.commitment_id
    assert commitment.proof_id == proof.proof_id
    assert commitment.proof_seal_digest
    assert commitment.audit_seal_id == audit_seal.seal_id
    assert commitment.finalization_id == finalization.finalization_id
    assert commitment.receipt_id == receipt.receipt_id


def test_tampered_commitment_is_rejected():
    bundle = _bundle()
    att, receipt, finalization, trail, audit_seal, proof = bundle
    commitment = issue_completion_proof_commitment(proof, audit_seal, finalization, receipt, "conv-1", "task-abc", "answer-abc", 3)
    commitment.answer_digest = "tampered"
    assert not commitment.valid(proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)


def test_upstream_proof_mutation_invalidates_commitment():
    bundle = _bundle()
    att, receipt, finalization, trail, audit_seal, proof = bundle
    commitment = issue_completion_proof_commitment(proof, audit_seal, finalization, receipt, "conv-1", "task-abc", "answer-abc", 3)
    proof.answer_digest = "tampered"
    assert not commitment.valid(proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)


def test_context_and_epoch_mismatch_are_rejected():
    bundle = _bundle()
    att, receipt, finalization, trail, audit_seal, proof = bundle
    commitment = issue_completion_proof_commitment(proof, audit_seal, finalization, receipt, "conv-1", "task-abc", "answer-abc", 3)
    assert not commitment.valid(proof, att, receipt, finalization, trail, audit_seal, "conv-2", "task-abc", "answer-abc", 3)
    assert not commitment.valid(proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-other", "answer-abc", 3)
    assert not commitment.valid(proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-other", 3)
    assert not commitment.valid(proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 4)


def test_serialization_restores_and_legacy_state_is_safe():
    bundle = _bundle()
    att, receipt, finalization, trail, audit_seal, proof = bundle
    commitment = issue_completion_proof_commitment(proof, audit_seal, finalization, receipt, "conv-1", "task-abc", "answer-abc", 3)
    restored = CompletionProofCommitment.from_dict(commitment.to_dict())
    assert restored is not None
    assert restored.valid(proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)
    assert CompletionProofCommitment.from_dict(None) is None
    assert CompletionProofCommitment.from_dict({"completion_proof_commitment_version": 999}) is None


def test_missing_or_invalid_upstream_cannot_create_commitment():
    bundle = _bundle()
    att, receipt, finalization, trail, audit_seal, proof = bundle
    assert issue_completion_proof_commitment(CompletionProofCommitment(), audit_seal, finalization, receipt, "conv-1", "task-abc", "answer-abc", 3).status == "not_required"
    proof.sealed = False
    assert issue_completion_proof_commitment(proof, audit_seal, finalization, receipt, "conv-1", "task-abc", "answer-abc", 3).status == "not_required"


def test_audit_seal_mutation_invalidates_commitment():
    bundle = _bundle()
    att, receipt, finalization, trail, audit_seal, proof = bundle
    commitment = issue_completion_proof_commitment(proof, audit_seal, finalization, receipt, "conv-1", "task-abc", "answer-abc", 3)
    audit_seal.answer_digest = "tampered"
    assert not commitment.valid(proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)


def main():
    tests = [
        ("commitment issues only from valid proof chain", test_commitment_issues_only_from_valid_proof_chain),
        ("commitment binds terminal identities", test_commitment_binds_terminal_identities),
        ("tampered commitment is rejected", test_tampered_commitment_is_rejected),
        ("upstream proof mutation invalidates commitment", test_upstream_proof_mutation_invalidates_commitment),
        ("context and epoch mismatch are rejected", test_context_and_epoch_mismatch_are_rejected),
        ("serialization restores and legacy state is safe", test_serialization_restores_and_legacy_state_is_safe),
        ("missing or invalid upstream cannot create commitment", test_missing_or_invalid_upstream_cannot_create_commitment),
        ("audit seal mutation invalidates commitment", test_audit_seal_mutation_invalidates_commitment),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.63 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test(); print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}"); raise SystemExit(1)
    print("\nSetup 4.63 tests complete.")


if __name__ == "__main__":
    main()
