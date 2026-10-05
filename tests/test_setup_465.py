"""Setup 4.65: terminal answer dispatch authorization tests."""
from services.completion_attestation import CompletionAttestation
from services.completion_receipt import issue_completion_receipt
from services.completion_finalization import issue_completion_finalization
from services.completion_audit import CompletionAuditTrail
from services.completion_audit_seal import issue_completion_audit_seal
from services.completion_proof import issue_completion_proof
from services.completion_proof_commitment import issue_completion_proof_commitment
from services.completion_release import issue_completion_release
from services.completion_dispatch import CompletionDispatch, issue_completion_dispatch


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
    release = issue_completion_release(commitment, proof, conv, task, answer, epoch)
    assert release.valid(commitment, proof, att, receipt, finalization, trail, audit_seal, conv, task, answer, epoch)
    assert release.consume()
    assert release.consumed_valid(commitment, proof, att, receipt, finalization, trail, audit_seal, conv, task, answer, epoch)
    return att, receipt, finalization, trail, audit_seal, proof, commitment, release


def test_dispatch_issues_only_from_consumed_release():
    att, receipt, finalization, trail, audit_seal, proof, commitment, release = _bundle()
    dispatch = issue_completion_dispatch(commitment=commitment, proof=proof, release=release, conversation_id="conv-1", task_digest="task-abc", answer_digest="answer-abc", change_epoch=3)
    assert dispatch.status == "authorized"
    assert dispatch.authorized and not dispatch.consumed


def test_dispatch_binds_terminal_identities():
    att, receipt, finalization, trail, audit_seal, proof, commitment, release = _bundle()
    dispatch = issue_completion_dispatch(release, commitment, proof, "conv-1", "task-abc", "answer-abc", 3)
    assert dispatch.release_id == release.release_id
    assert dispatch.release_seal_digest
    assert dispatch.commitment_id == commitment.commitment_id
    assert dispatch.proof_id == proof.proof_id
    assert dispatch.answer_digest == "answer-abc"


def test_tampered_dispatch_is_rejected():
    att, receipt, finalization, trail, audit_seal, proof, commitment, release = _bundle()
    dispatch = issue_completion_dispatch(release, commitment, proof, "conv-1", "task-abc", "answer-abc", 3)
    dispatch.answer_digest = "tampered"
    assert not dispatch.valid(release, commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)


def test_upstream_release_mutation_invalidates_dispatch():
    att, receipt, finalization, trail, audit_seal, proof, commitment, release = _bundle()
    dispatch = issue_completion_dispatch(release, commitment, proof, "conv-1", "task-abc", "answer-abc", 3)
    release.answer_digest = "tampered"
    assert not dispatch.valid(release, commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)


def test_context_and_epoch_mismatch_are_rejected():
    att, receipt, finalization, trail, audit_seal, proof, commitment, release = _bundle()
    dispatch = issue_completion_dispatch(release, commitment, proof, "conv-1", "task-abc", "answer-abc", 3)
    assert not dispatch.valid(release, commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-2", "task-abc", "answer-abc", 3)
    assert not dispatch.valid(release, commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-other", "answer-abc", 3)
    assert not dispatch.valid(release, commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-other", 3)
    assert not dispatch.valid(release, commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 4)


def test_consume_is_one_time_and_integrity_survives():
    att, receipt, finalization, trail, audit_seal, proof, commitment, release = _bundle()
    dispatch = issue_completion_dispatch(release, commitment, proof, "conv-1", "task-abc", "answer-abc", 3)
    assert dispatch.valid(release, commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)
    old_seal = dispatch.seal
    assert dispatch.consume()
    assert not dispatch.consume()
    assert dispatch.consumed
    assert dispatch.seal != old_seal
    assert not dispatch.valid(release, commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)
    assert dispatch.consumed_valid(release, commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)


def test_serialization_and_legacy_state_are_safe():
    att, receipt, finalization, trail, audit_seal, proof, commitment, release = _bundle()
    dispatch = issue_completion_dispatch(release, commitment, proof, "conv-1", "task-abc", "answer-abc", 3)
    restored = CompletionDispatch.from_dict(dispatch.to_dict())
    assert restored is not None
    assert restored.valid(release, commitment, proof, att, receipt, finalization, trail, audit_seal, "conv-1", "task-abc", "answer-abc", 3)
    assert CompletionDispatch.from_dict(None) is None
    assert CompletionDispatch.from_dict({"completion_dispatch_version": 999}) is None


def test_missing_upstream_cannot_create_dispatch():
    dispatch = issue_completion_dispatch(CompletionDispatch(), None, None, "conv-1", "task-abc", "answer-abc", 3)
    assert dispatch.status == "not_required"
    att, receipt, finalization, trail, audit_seal, proof, commitment, release = _bundle()
    release.consumed = False
    dispatch = issue_completion_dispatch(release, commitment, proof, "conv-1", "task-abc", "answer-abc", 3)
    assert dispatch.status == "not_required"


def main():
    tests = [
        ("dispatch issues only from consumed release", test_dispatch_issues_only_from_consumed_release),
        ("dispatch binds terminal identities", test_dispatch_binds_terminal_identities),
        ("tampered dispatch is rejected", test_tampered_dispatch_is_rejected),
        ("upstream release mutation invalidates dispatch", test_upstream_release_mutation_invalidates_dispatch),
        ("context and epoch mismatch are rejected", test_context_and_epoch_mismatch_are_rejected),
        ("consume is one-time and integrity survives", test_consume_is_one_time_and_integrity_survives),
        ("serialization and legacy state are safe", test_serialization_and_legacy_state_are_safe),
        ("missing upstream cannot create dispatch", test_missing_upstream_cannot_create_dispatch),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.65 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test(); print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}"); raise SystemExit(1)
    print("\nSetup 4.65 tests complete.")

if __name__ == "__main__":
    main()
