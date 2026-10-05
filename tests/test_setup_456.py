"""Setup 4.56 final-answer-bound completion attestation tests."""
from services.completion_attestation import (
    CompletionAttestation,
    answer_identity_digest,
    build_policy_identity,
    build_task_identity,
    change_plan_identity_digest,
    create_attestation,
)
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.evidence_recovery import EvidenceRecoveryPlan
from services.impact_verification import ImpactVerification
from services.task_planner import TaskPlan, PlanStep
from services.change_planner import ChangePlan

CAPS = [{"name": "write_file", "arguments": [{"name": "path", "required": True, "type": "string"}]}]
RUNTIME = {"backend": "LMStudioGateway", "model": "qwen/qwen3.5-9b", "endpoint": "http://localhost:1234/v1"}
IDENTITY = build_task_identity("edit app/a.py", "conv-1", 2)
PLAN = TaskPlan("edit app/a.py", [PlanStep("S1", "Inspect", "Inspect app/a.py", []), PlanStep("S2", "Edit", "Edit app/a.py", ["S1"])])
RECOVERY = EvidenceRecoveryPlan("complete", [], [], ["Completion evidence is already sufficient."])
POLICY = build_policy_identity(16)
CHANGE_PLAN = ChangePlan(
    targets=["app/a.py"],
    inspect_paths=["lib/base.py", "app/a.py"],
    change_paths=["app/a.py"],
    verify_paths=["app/a.py", "app/main.py"],
    dependency_paths=["lib/base.py"],
    dependent_paths=["app/main.py"],
    rationale=["stable rationale"],
)
SUCCESS = ["write_file|{\"path\":\"app/a.py\"}", "read_file|{\"path\":\"app/a.py\"}"]
FAILED = ["run_command|{\"command\":\"bad\"}"]
ANSWER = "Updated app/a.py and verified the affected resources successfully."


def _ready():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("write_file", "modification", "app/a.py", {"ok": True}, 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app/a.py", {"ok": True}, 1, 1))
    verification = ImpactVerification(["app/a.py"], ["app/a.py"], [], "complete", "verified")
    ledger.evaluate(verification, True, 1, {"app/a.py": 1})
    return ledger, verification


def _att(answer=ANSWER):
    ledger, verification = _ready()
    att = create_attestation(
        ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME,
        None, PLAN, RECOVERY, POLICY, SUCCESS, FAILED, CHANGE_PLAN, answer
    )
    return ledger, verification, att


def _valid(att, ledger, verification, answer=ANSWER):
    return att.valid(
        ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME,
        None, PLAN, RECOVERY, POLICY, SUCCESS, FAILED, CHANGE_PLAN, answer
    )


def test_answer_bound_attestation_validates():
    ledger, verification, att = _att()
    assert att.status == "sealed"
    assert att.answer_digest == answer_identity_digest(ANSWER)
    assert _valid(att, ledger, verification)


def test_changed_final_answer_invalidates_attestation():
    ledger, verification, att = _att()
    changed = "Updated the file, but verification is still pending."
    assert answer_identity_digest(changed) != att.answer_digest
    assert not _valid(att, ledger, verification, changed)


def test_answer_digest_ignores_outer_whitespace_but_preserves_content():
    assert answer_identity_digest("  hello world  ") == answer_identity_digest("hello world")
    assert answer_identity_digest("hello world") != answer_identity_digest("hello  world")
    assert answer_identity_digest("") == ""


def test_legacy_setup_455_attestation_restores_without_answer_binding():
    restored = CompletionAttestation.from_dict({"attestation_version": 10, "status": "sealed", "seal": "legacy"})
    assert restored is not None
    assert restored.answer_digest == ""


def test_missing_answer_cannot_reuse_new_answer_bound_attestation():
    ledger, verification, att = _att()
    assert att.answer_digest
    assert not _valid(att, ledger, verification, None)


def test_same_answer_with_other_bound_state_still_validates():
    ledger, verification, att = _att()
    assert att.change_plan_digest == change_plan_identity_digest(CHANGE_PLAN)
    assert _valid(att, ledger, verification, "  " + ANSWER + "  ")


def main():
    tests = [
        ("answer-bound attestation validates", test_answer_bound_attestation_validates),
        ("changed final answer invalidates attestation", test_changed_final_answer_invalidates_attestation),
        ("answer digest ignores outer whitespace but preserves content", test_answer_digest_ignores_outer_whitespace_but_preserves_content),
        ("legacy Setup 4.55 attestation restores without answer binding", test_legacy_setup_455_attestation_restores_without_answer_binding),
        ("missing answer cannot reuse new answer-bound attestation", test_missing_answer_cannot_reuse_new_answer_bound_attestation),
        ("same answer with other bound state still validates", test_same_answer_with_other_bound_state_still_validates),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.56 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test()
            print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            raise SystemExit(1)
    print("\nSetup 4.56 tests complete.")

if __name__ == "__main__":
    main()
