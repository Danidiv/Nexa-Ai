"""Setup 4.54 execution-history-bound completion attestation tests."""
from services.completion_attestation import (
    CompletionAttestation,
    build_policy_identity,
    create_attestation,
    execution_history_identity_digest,
    build_task_identity,
)
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.evidence_recovery import EvidenceRecoveryPlan
from services.impact_verification import ImpactVerification
from services.task_planner import TaskPlan, PlanStep

CAPS = [{"name": "write_file", "arguments": [{"name": "path", "required": True, "type": "string"}]}]
RUNTIME = {"backend": "LMStudioGateway", "model": "qwen/qwen3.5-9b", "endpoint": "http://localhost:1234/v1"}
IDENTITY = build_task_identity("edit app/a.py", "conv-1", 2)
PLAN = TaskPlan("edit app/a.py", [PlanStep("S1", "Inspect", "Inspect app/a.py", []), PlanStep("S2", "Edit", "Edit app/a.py", ["S1"])])
RECOVERY = EvidenceRecoveryPlan("complete", [], [], ["Completion evidence is already sufficient."])
POLICY = build_policy_identity(16)
SUCCESS = ["write_file|{\"path\":\"app/a.py\"}", "read_file|{\"path\":\"app/a.py\"}"]
FAILED = ["run_command|{\"command\":\"bad\"}"]


def _ready():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("write_file", "modification", "app/a.py", {"ok": True}, 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app/a.py", {"ok": True}, 1, 1))
    verification = ImpactVerification(["app/a.py"], ["app/a.py"], [], "complete", "verified")
    ledger.evaluate(verification, True, 1, {"app/a.py": 1})
    return ledger, verification


def _att(success=SUCCESS, failed=FAILED):
    ledger, verification = _ready()
    att = create_attestation(
        ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME,
        None, PLAN, RECOVERY, POLICY, success, failed
    )
    return ledger, verification, att


def test_execution_history_bound_attestation_validates():
    ledger, verification, att = _att()
    assert att.status == "sealed"
    assert att.execution_history_digest == execution_history_identity_digest(SUCCESS, FAILED)
    assert att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY, POLICY, SUCCESS, FAILED)


def test_changed_execution_history_invalidates_attestation():
    ledger, verification, att = _att()
    changed = list(SUCCESS)
    changed[0] = "write_file|{\"path\":\"app/b.py\"}"
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY, POLICY, changed, FAILED)


def test_execution_history_digest_is_deterministic_bounded_and_secret_safe():
    a = execution_history_identity_digest(SUCCESS, FAILED)
    b = execution_history_identity_digest(tuple(SUCCESS), tuple(FAILED))
    assert a == b
    assert len(a) == 24
    assert execution_history_identity_digest([], []) == ""
    assert "app/a.py" not in a
    assert "bad" not in a


def test_legacy_setup_453_attestation_restores_without_execution_history_binding():
    restored = CompletionAttestation.from_dict({"attestation_version": 8, "status": "sealed", "seal": "legacy"})
    assert restored is not None
    assert restored.execution_history_digest == ""


def test_reordered_execution_history_invalidates_attestation():
    ledger, verification, att = _att()
    reordered = list(reversed(SUCCESS))
    assert execution_history_identity_digest(reordered, FAILED) != att.execution_history_digest
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY, POLICY, reordered, FAILED)


def test_failed_history_change_invalidates_attestation():
    ledger, verification, att = _att()
    changed_failed = FAILED + ["run_python|{\"path\":\"bad.py\"}"]
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY, POLICY, SUCCESS, changed_failed)


def main():
    tests = [
        ("execution-history-bound attestation validates", test_execution_history_bound_attestation_validates),
        ("changed execution history invalidates attestation", test_changed_execution_history_invalidates_attestation),
        ("execution history digest is deterministic bounded and secret-safe", test_execution_history_digest_is_deterministic_bounded_and_secret_safe),
        ("legacy Setup 4.53 attestation restores without execution-history binding", test_legacy_setup_453_attestation_restores_without_execution_history_binding),
        ("reordered execution history invalidates attestation", test_reordered_execution_history_invalidates_attestation),
        ("failed history change invalidates attestation", test_failed_history_change_invalidates_attestation),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.54 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test()
            print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            raise SystemExit(1)
    print("\nSetup 4.54 tests complete.")

if __name__ == "__main__":
    main()
