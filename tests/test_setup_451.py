"""Setup 4.51 recovery-bound completion attestation tests."""
from services.completion_attestation import CompletionAttestation, build_task_identity, create_attestation, recovery_identity_digest
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.evidence_recovery import EvidenceRecoveryPlan
from services.impact_verification import ImpactVerification
from services.task_planner import TaskPlan, PlanStep

CAPS = [{"name": "write_file", "arguments": [{"name": "path", "required": True, "type": "string"}]}]
RUNTIME = {"backend": "LMStudioGateway", "model": "qwen/qwen3.5-9b", "endpoint": "http://localhost:1234/v1"}
IDENTITY = build_task_identity("edit app/a.py", "conv-1", 2)
PLAN = TaskPlan("edit app/a.py", [
    PlanStep("S1", "Inspect", "Inspect app/a.py", []),
    PlanStep("S2", "Edit", "Edit app/a.py", ["S1"]),
])
RECOVERY = EvidenceRecoveryPlan("complete", [], [], ["Completion evidence is already sufficient."])


def _ready():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("write_file", "modification", "app/a.py", {"ok": True}, 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app/a.py", {"ok": True}, 1, 1))
    verification = ImpactVerification(["app/a.py"], ["app/a.py"], [], "complete", "verified")
    ledger.evaluate(verification, True, 1, {"app/a.py": 1})
    return ledger, verification


def _att(recovery=RECOVERY):
    ledger, verification = _ready()
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, recovery)
    return ledger, verification, att


def test_recovery_bound_attestation_validates():
    ledger, verification, att = _att()
    assert att.status == "sealed"
    assert att.recovery_digest == recovery_identity_digest(RECOVERY)
    assert att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY)


def test_changed_recovery_status_invalidates_attestation():
    ledger, verification, att = _att()
    changed = EvidenceRecoveryPlan("pending", [{"recovery_version": 1, "item_id": "verify:app/a.py", "kind": "verification", "target": "app/a.py", "objective": "Verify app/a.py", "status": "pending"}], ["verification evidence for app/a.py"], [])
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, changed)


def test_recovery_digest_is_deterministic_and_ignores_rationale():
    a = EvidenceRecoveryPlan("complete", [], [], ["one"])
    b = EvidenceRecoveryPlan("complete", [], [], ["different wording"])
    assert recovery_identity_digest(a) == recovery_identity_digest(b)
    assert len(recovery_identity_digest(a)) == 24


def test_legacy_setup_450_attestation_restores_without_recovery_binding():
    restored = CompletionAttestation.from_dict({"attestation_version": 5, "status": "not_required"})
    assert restored is not None
    assert restored.recovery_digest == ""


def test_missing_recovery_identity_cannot_reuse_new_attestation():
    ledger, verification, att = _att()
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, None)


def test_recovery_item_change_invalidates_even_when_status_same():
    ledger, verification, att = _att()
    changed = EvidenceRecoveryPlan("complete", [{"recovery_version": 1, "item_id": "verify:app/a.py", "kind": "verification", "target": "app/a.py", "objective": "Verify app/a.py", "status": "complete"}], [], [])
    assert changed.status == RECOVERY.status
    assert recovery_identity_digest(changed) != att.recovery_digest
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, changed)


def main():
    tests = [
        ("recovery-bound attestation validates", test_recovery_bound_attestation_validates),
        ("changed recovery status invalidates attestation", test_changed_recovery_status_invalidates_attestation),
        ("recovery digest is deterministic and ignores rationale", test_recovery_digest_is_deterministic_and_ignores_rationale),
        ("legacy Setup 4.50 attestation restores without recovery binding", test_legacy_setup_450_attestation_restores_without_recovery_binding),
        ("missing recovery identity cannot reuse new attestation", test_missing_recovery_identity_cannot_reuse_new_attestation),
        ("recovery item change invalidates even when status same", test_recovery_item_change_invalidates_even_when_status_same),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.51 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test()
            print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            raise SystemExit(1)
    print("\nSetup 4.51 tests complete.")

if __name__ == "__main__":
    main()
