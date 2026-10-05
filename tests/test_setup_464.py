"""Setup 4.64: one-time final-answer release token tests."""
from services.completion_attestation import CompletionAttestation
from services.completion_receipt import issue_completion_receipt
from services.completion_finalization import issue_completion_finalization
from services.completion_audit import CompletionAuditTrail
from services.completion_audit_seal import issue_completion_audit_seal
from services.completion_proof import issue_completion_proof
from services.completion_proof_commitment import issue_completion_proof_commitment
from services.completion_release import CompletionRelease, issue_completion_release


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
    assert proof.valid(att, receipt, finalization, trail, audit_seal, conv, task, answer, epoch)
    commitment = issue_completion_proof_commitment(proof, audit_seal, finalization, receipt, conv, task, answer, epoch)
    assert commitment.valid(proof, att, receipt, finalization, trail, audit_seal, conv, task, answer, epoch)
    return att, receipt, finalization, trail, audit_seal, proof, commitment


def test_release_issues_only_from_valid_commitment():
    att, receipt, finalization, trail, audit_seal, proof, commitment = _bundle()
    release = issue_completion_release(commitment, proof, "conv-1", "task-abc", "answer-abc", 3)
    assert release.status == "released"
    assert release.released and not release.consumed
    assert release.valid(commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)


def test_release_binds_terminal_identities():
    att, receipt, finalization, trail, audit_seal, proof, commitment = _bundle()
    release = issue_completion_release(commitment, proof, "conv-1", "task-abc", "answer-abc", 3)
    assert release.release_id
    assert release.commitment_id == commitment.commitment_id
    assert release.commitment_seal_digest
    assert release.proof_id == proof.proof_id
    assert release.answer_digest == "answer-abc"


def test_tampered_release_is_rejected():
    att, receipt, finalization, trail, audit_seal, proof, commitment = _bundle()
    release = issue_completion_release(commitment, proof, "conv-1", "task-abc", "answer-abc", 3)
    release.answer_digest = "tampered"
    assert not release.valid(commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)


def test_upstream_commitment_mutation_invalidates_release():
    att, receipt, finalization, trail, audit_seal, proof, commitment = _bundle()
    release = issue_completion_release(commitment, proof, "conv-1", "task-abc", "answer-abc", 3)
    commitment.answer_digest = "tampered"
    assert not release.valid(commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)


def test_context_and_epoch_mismatch_are_rejected():
    att, receipt, finalization, trail, audit_seal, proof, commitment = _bundle()
    release = issue_completion_release(commitment, proof, "conv-1", "task-abc", "answer-abc", 3)
    assert not release.valid(commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-2", "task-abc", "answer-abc", 3)
    assert not release.valid(commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-other", "answer-abc", 3)
    assert not release.valid(commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-other", 3)
    assert not release.valid(commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 4)


def test_consume_is_one_time_and_consumed_integrity_survives():
    att, receipt, finalization, trail, audit_seal, proof, commitment = _bundle()
    release = issue_completion_release(commitment, proof, "conv-1", "task-abc", "answer-abc", 3)
    assert release.consume()
    assert not release.consume()
    assert release.consumed
    assert not release.valid(commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)
    assert release.consumed_valid(commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)


def test_serialization_and_legacy_state_are_safe():
    att, receipt, finalization, trail, audit_seal, proof, commitment = _bundle()
    release = issue_completion_release(commitment, proof, "conv-1", "task-abc", "answer-abc", 3)
    restored = CompletionRelease.from_dict(release.to_dict())
    assert restored is not None
    assert restored.valid(commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)
    assert CompletionRelease.from_dict(None) is None
    assert CompletionRelease.from_dict({"completion_release_version": 999}) is None


def test_missing_upstream_cannot_create_release():
    release = issue_completion_release(CompletionRelease(), None, "conv-1", "task-abc", "answer-abc", 3)
    assert release.status == "not_required"
    att, receipt, finalization, trail, audit_seal, proof, commitment = _bundle()
    commitment.committed = False
    release = issue_completion_release(commitment, proof, "conv-1", "task-abc", "answer-abc", 3)
    assert release.status == "not_required"


def main():
    tests = [
        ("release issues only from valid commitment", test_release_issues_only_from_valid_commitment),
        ("release binds terminal identities", test_release_binds_terminal_identities),
        ("tampered release is rejected", test_tampered_release_is_rejected),
        ("upstream commitment mutation invalidates release", test_upstream_commitment_mutation_invalidates_release),
        ("context and epoch mismatch are rejected", test_context_and_epoch_mismatch_are_rejected),
        ("consume is one-time and consumed integrity survives", test_consume_is_one_time_and_consumed_integrity_survives),
        ("serialization and legacy state are safe", test_serialization_and_legacy_state_are_safe),
        ("missing upstream cannot create release", test_missing_upstream_cannot_create_release),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.64 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test(); print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}"); raise SystemExit(1)
    print("\nSetup 4.64 tests complete.")

if __name__ == "__main__":
    main()
