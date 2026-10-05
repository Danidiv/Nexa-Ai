"""Setup 4.52 impact-verification-bound completion attestation tests."""
from services.completion_attestation import CompletionAttestation, create_attestation, verification_identity_digest, build_task_identity
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.evidence_recovery import EvidenceRecoveryPlan
from services.impact_verification import ImpactVerification
from services.task_planner import TaskPlan, PlanStep

CAPS = [{"name": "write_file", "arguments": [{"name": "path", "required": True, "type": "string"}]}]
RUNTIME = {"backend": "LMStudioGateway", "model": "qwen/qwen3.5-9b", "endpoint": "http://localhost:1234/v1"}
IDENTITY = build_task_identity("edit app/a.py", "conv-1", 2)
PLAN = TaskPlan("edit app/a.py", [PlanStep("S1", "Inspect", "Inspect app/a.py", []), PlanStep("S2", "Edit", "Edit app/a.py", ["S1"])])
RECOVERY = EvidenceRecoveryPlan("complete", [], [], ["Completion evidence is already sufficient."])


def _ready():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("write_file", "modification", "app/a.py", {"ok": True}, 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app/a.py", {"ok": True}, 1, 1))
    verification = ImpactVerification(["app/a.py"], ["app/a.py"], [], "complete", "verified")
    ledger.evaluate(verification, True, 1, {"app/a.py": 1})
    return ledger, verification


def _att(verification=None):
    ledger, current = _ready()
    verification = verification or current
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY)
    return ledger, verification, att


def test_verification_bound_attestation_validates():
    ledger, verification, att = _att()
    assert att.status == "sealed"
    assert att.verification_digest == verification_identity_digest(verification)
    assert att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY)


def test_completed_paths_change_invalidates_attestation():
    ledger, verification, att = _att()
    changed = ImpactVerification(["app/a.py"], [], ["app/a.py"], "complete", "still complete")
    assert not att.valid(ledger, changed, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY)


def test_verification_digest_is_deterministic_and_ignores_rationale():
    a = ImpactVerification(["b.py", "a.py"], ["a.py"], [], "complete", "one")
    b = ImpactVerification(["a.py", "b.py"], ["a.py"], [], "complete", "different wording")
    assert verification_identity_digest(a) == verification_identity_digest(b)
    assert len(verification_identity_digest(a)) == 24


def test_legacy_setup_451_attestation_restores_without_verification_binding():
    restored = CompletionAttestation.from_dict({"attestation_version": 6, "status": "not_required"})
    assert restored is not None
    assert restored.verification_digest == ""


def test_missing_verification_identity_cannot_reuse_new_attestation():
    ledger, verification, att = _att()
    assert not att.valid(ledger, None, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY)


def test_missing_paths_change_invalidates_even_when_status_same():
    ledger, verification, att = _att()
    changed = ImpactVerification(["app/a.py"], ["app/a.py"], ["other.py"], "complete", "complete")
    assert changed.status == verification.status
    assert verification_identity_digest(changed) != att.verification_digest
    assert not att.valid(ledger, changed, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY)


def main():
    tests = [
        ("verification-bound attestation validates", test_verification_bound_attestation_validates),
        ("changed completed paths invalidate attestation", test_completed_paths_change_invalidates_attestation),
        ("verification digest is deterministic and ignores rationale", test_verification_digest_is_deterministic_and_ignores_rationale),
        ("legacy Setup 4.51 attestation restores without verification binding", test_legacy_setup_451_attestation_restores_without_verification_binding),
        ("missing verification identity cannot reuse new attestation", test_missing_verification_identity_cannot_reuse_new_attestation),
        ("missing paths change invalidates even when status same", test_missing_paths_change_invalidates_even_when_status_same),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.52 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test()
            print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            raise SystemExit(1)
    print("\nSetup 4.52 tests complete.")

if __name__ == "__main__":
    main()
