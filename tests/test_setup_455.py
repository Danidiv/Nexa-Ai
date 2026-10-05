"""Setup 4.55 change-plan-bound completion attestation tests."""
from services.completion_attestation import (
    CompletionAttestation,
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


def _ready():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("write_file", "modification", "app/a.py", {"ok": True}, 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app/a.py", {"ok": True}, 1, 1))
    verification = ImpactVerification(["app/a.py"], ["app/a.py"], [], "complete", "verified")
    ledger.evaluate(verification, True, 1, {"app/a.py": 1})
    return ledger, verification


def _att(change_plan=CHANGE_PLAN):
    ledger, verification = _ready()
    att = create_attestation(
        ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME,
        None, PLAN, RECOVERY, POLICY, SUCCESS, FAILED, change_plan
    )
    return ledger, verification, att


def test_change_plan_bound_attestation_validates():
    ledger, verification, att = _att()
    assert att.status == "sealed"
    assert att.change_plan_digest == change_plan_identity_digest(CHANGE_PLAN)
    assert att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME,
                      None, PLAN, RECOVERY, POLICY, SUCCESS, FAILED, CHANGE_PLAN)


def test_changed_change_scope_invalidates_attestation():
    ledger, verification, att = _att()
    changed = ChangePlan(
        targets=["app/a.py"], inspect_paths=["lib/other.py", "app/a.py"],
        change_paths=["app/a.py"], verify_paths=["app/a.py", "app/main.py"],
        dependency_paths=["lib/other.py"], dependent_paths=["app/main.py"], rationale=["stable rationale"]
    )
    assert change_plan_identity_digest(changed) != att.change_plan_digest
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME,
                         None, PLAN, RECOVERY, POLICY, SUCCESS, FAILED, changed)


def test_change_plan_digest_is_deterministic_and_ignores_rationale():
    a = change_plan_identity_digest(CHANGE_PLAN)
    changed_rationale = ChangePlan(
        targets=list(reversed(CHANGE_PLAN.targets)), inspect_paths=list(reversed(CHANGE_PLAN.inspect_paths)),
        change_paths=list(reversed(CHANGE_PLAN.change_paths)), verify_paths=list(reversed(CHANGE_PLAN.verify_paths)),
        dependency_paths=list(reversed(CHANGE_PLAN.dependency_paths)), dependent_paths=list(reversed(CHANGE_PLAN.dependent_paths)),
        rationale=["completely different wording"],
    )
    assert a == change_plan_identity_digest(changed_rationale)
    assert len(a) == 24
    assert change_plan_identity_digest(None) == ""


def test_legacy_setup_454_attestation_restores_without_change_plan_binding():
    restored = CompletionAttestation.from_dict({"attestation_version": 9, "status": "sealed", "seal": "legacy"})
    assert restored is not None
    assert restored.change_plan_digest == ""


def test_missing_change_plan_identity_cannot_reuse_new_attestation():
    ledger, verification, att = _att()
    assert att.change_plan_digest
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME,
                         None, PLAN, RECOVERY, POLICY, SUCCESS, FAILED, None)


def test_change_plan_structure_change_invalidates_even_if_rationale_same():
    ledger, verification, att = _att()
    changed = ChangePlan(
        targets=["app/a.py"], inspect_paths=CHANGE_PLAN.inspect_paths,
        change_paths=["app/a.py", "app/helper.py"], verify_paths=CHANGE_PLAN.verify_paths,
        dependency_paths=CHANGE_PLAN.dependency_paths, dependent_paths=CHANGE_PLAN.dependent_paths,
        rationale=CHANGE_PLAN.rationale,
    )
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME,
                         None, PLAN, RECOVERY, POLICY, SUCCESS, FAILED, changed)


def main():
    tests = [
        ("change-plan-bound attestation validates", test_change_plan_bound_attestation_validates),
        ("changed change scope invalidates attestation", test_changed_change_scope_invalidates_attestation),
        ("change-plan digest is deterministic and ignores rationale", test_change_plan_digest_is_deterministic_and_ignores_rationale),
        ("legacy Setup 4.54 attestation restores without change-plan binding", test_legacy_setup_454_attestation_restores_without_change_plan_binding),
        ("missing change-plan identity cannot reuse new attestation", test_missing_change_plan_identity_cannot_reuse_new_attestation),
        ("change-plan structure change invalidates even if rationale same", test_change_plan_structure_change_invalidates_even_if_rationale_same),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.55 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test()
            print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            raise SystemExit(1)
    print("\nSetup 4.55 tests complete.")

if __name__ == "__main__":
    main()
