"""Setup 4.53 policy-bound completion attestation tests."""
from services.completion_attestation import (
    CompletionAttestation,
    build_policy_identity,
    create_attestation,
    policy_identity_digest,
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


def _ready():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("write_file", "modification", "app/a.py", {"ok": True}, 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app/a.py", {"ok": True}, 1, 1))
    verification = ImpactVerification(["app/a.py"], ["app/a.py"], [], "complete", "verified")
    ledger.evaluate(verification, True, 1, {"app/a.py": 1})
    return ledger, verification


def _att(policy=POLICY):
    ledger, verification = _ready()
    att = create_attestation(
        ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME,
        None, PLAN, RECOVERY, policy
    )
    return ledger, verification, att


def test_policy_bound_attestation_validates():
    ledger, verification, att = _att()
    assert att.status == "sealed"
    assert att.policy_digest == policy_identity_digest(POLICY)
    assert att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY, POLICY)


def test_changed_policy_invalidates_attestation():
    ledger, verification, att = _att()
    changed = dict(POLICY)
    changed["max_steps"] = 32
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY, changed)


def test_policy_digest_is_deterministic_and_bounded():
    a = {"b": "two", "a": "one", "max_steps": 16}
    b = {"max_steps": 16, "a": "one", "b": "two"}
    digest = policy_identity_digest(a)
    assert digest == policy_identity_digest(b)
    assert len(digest) == 24
    assert policy_identity_digest({}) == ""


def test_legacy_setup_452_attestation_restores_without_policy_binding():
    restored = CompletionAttestation.from_dict({"attestation_version": 7, "status": "sealed", "seal": "legacy"})
    assert restored is not None
    assert restored.policy_digest == ""


def test_missing_policy_identity_cannot_reuse_new_attestation():
    ledger, verification, att = _att()
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY, None)


def test_policy_structure_change_invalidates_even_when_version_same():
    ledger, verification, att = _att()
    changed = dict(POLICY)
    changed["read_after_modify"] = False
    assert policy_identity_digest(changed) != att.policy_digest
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY, changed)


def main():
    tests = [
        ("policy-bound attestation validates", test_policy_bound_attestation_validates),
        ("changed policy invalidates attestation", test_changed_policy_invalidates_attestation),
        ("policy digest is deterministic and bounded", test_policy_digest_is_deterministic_and_bounded),
        ("legacy Setup 4.52 attestation restores without policy binding", test_legacy_setup_452_attestation_restores_without_policy_binding),
        ("missing policy identity cannot reuse new attestation", test_missing_policy_identity_cannot_reuse_new_attestation),
        ("policy structure change invalidates even when version same", test_policy_structure_change_invalidates_even_when_version_same),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.53 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test()
            print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            raise SystemExit(1)
    print("\nSetup 4.53 tests complete.")

if __name__ == "__main__":
    main()
