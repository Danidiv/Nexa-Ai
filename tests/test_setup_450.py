"""Setup 4.50 plan-bound completion attestation tests."""
from services.completion_attestation import CompletionAttestation, build_task_identity, create_attestation, plan_identity_digest
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.impact_verification import ImpactVerification
from services.task_planner import TaskPlan, PlanStep

CAPS = [{"name": "write_file", "arguments": [{"name": "path", "required": True, "type": "string"}]}]
RUNTIME = {"backend": "LMStudioGateway", "model": "qwen/qwen3.5-9b", "endpoint": "http://localhost:1234/v1"}
IDENTITY = build_task_identity("edit app/a.py", "conv-1", 2)
PLAN = TaskPlan("edit app/a.py", [
    PlanStep("S1", "Inspect", "Inspect app/a.py", []),
    PlanStep("S2", "Edit", "Edit app/a.py", ["S1"]),
])


def _ready():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("write_file", "modification", "app/a.py", {"ok": True}, 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app/a.py", {"ok": True}, 1, 1))
    verification = ImpactVerification(["app/a.py"], ["app/a.py"], [], "complete", "verified")
    ledger.evaluate(verification, True, 1, {"app/a.py": 1})
    return ledger, verification


def _att():
    ledger, verification = _ready()
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN)
    return ledger, verification, att


def test_plan_bound_attestation_validates():
    ledger, verification, att = _att()
    assert att.status == "sealed"
    assert att.plan_digest == plan_identity_digest(PLAN)
    assert att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN)


def test_changed_plan_objective_invalidates_attestation():
    ledger, verification, att = _att()
    changed = TaskPlan("edit app/a.py", [
        PlanStep("S1", "Inspect", "Inspect app/a.py", []),
        PlanStep("S2", "Edit", "Replace app/a.py completely", ["S1"]),
    ])
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, changed)


def test_plan_digest_is_deterministic_and_ignores_step_status():
    a = TaskPlan("edit app/a.py", [PlanStep("S2", "Edit", "Edit", ["S1"], "pending"), PlanStep("S1", "Inspect", "Inspect", [])])
    b = TaskPlan("edit app/a.py", [PlanStep("S1", "Inspect", "Inspect", [], "completed"), PlanStep("S2", "Edit", "Edit", ["S1"], "in_progress")])
    assert plan_identity_digest(a) == plan_identity_digest(b)
    assert len(plan_identity_digest(a)) == 24


def test_legacy_setup_449_attestation_restores_without_plan_binding():
    restored = CompletionAttestation.from_dict({"attestation_version": 4, "status": "not_required"})
    assert restored is not None
    assert restored.plan_digest == ""


def test_missing_plan_identity_cannot_reuse_new_attestation():
    ledger, verification, att = _att()
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, None)


def test_plan_structure_change_invalidates_even_same_revision():
    ledger, verification, att = _att()
    changed = TaskPlan("edit app/a.py", [
        PlanStep("S1", "Inspect", "Inspect app/a.py", []),
        PlanStep("S2", "Edit", "Edit app/a.py", ["S1", "S3"]),
        PlanStep("S3", "Extra", "Inspect related file", []),
    ])
    changed.revision = PLAN.revision
    assert changed.revision == PLAN.revision
    assert plan_identity_digest(changed) != att.plan_digest
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, changed)


def main():
    tests = [
        ("plan-bound attestation validates", test_plan_bound_attestation_validates),
        ("changed plan objective invalidates attestation", test_changed_plan_objective_invalidates_attestation),
        ("plan digest is deterministic and ignores step status", test_plan_digest_is_deterministic_and_ignores_step_status),
        ("legacy Setup 4.49 attestation restores without plan binding", test_legacy_setup_449_attestation_restores_without_plan_binding),
        ("missing plan identity cannot reuse new attestation", test_missing_plan_identity_cannot_reuse_new_attestation),
        ("plan structure change invalidates even with same revision", test_plan_structure_change_invalidates_even_same_revision),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.50 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test()
            print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            raise SystemExit(1)
    print("\nSetup 4.50 tests complete.")

if __name__ == "__main__":
    main()
