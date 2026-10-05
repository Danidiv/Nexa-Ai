"""Setup 4.46 task-bound completion attestation tests."""
from services.completion_attestation import (
    CompletionAttestation,
    build_task_identity,
    create_attestation,
    task_identity_digest,
)
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.impact_verification import ImpactVerification


def _ready():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("write_file", "modification", "app/a.py", {"ok": True}, 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app/a.py", {"ok": True}, 1, 1))
    verification = ImpactVerification(["app/a.py"], ["app/a.py"], [], "complete", "verified")
    ledger.evaluate(verification, True, 1, {"app/a.py": 1})
    return ledger, verification


def test_task_bound_attestation_validates():
    ledger, verification = _ready()
    identity = build_task_identity("edit app/a.py", "conv-1", 2)
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1}, identity)
    assert att.status == "sealed"
    assert att.task_digest == task_identity_digest(identity)
    assert att.valid(ledger, verification, 1, {"app/a.py": 1}, identity)


def test_different_conversation_cannot_reuse_attestation():
    ledger, verification = _ready()
    identity = build_task_identity("edit app/a.py", "conv-1", 2)
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1}, identity)
    other = build_task_identity("edit app/a.py", "conv-2", 2)
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, other)


def test_different_original_task_cannot_reuse_attestation():
    ledger, verification = _ready()
    identity = build_task_identity("edit app/a.py", "conv-1", 2)
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1}, identity)
    other = build_task_identity("delete app/a.py", "conv-1", 2)
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, other)


def test_plan_revision_change_invalidates_attestation():
    ledger, verification = _ready()
    identity = build_task_identity("edit app/a.py", "conv-1", 2)
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1}, identity)
    other = build_task_identity("edit app/a.py", "conv-1", 3)
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, other)


def test_legacy_setup_445_attestation_restores_safely():
    restored = CompletionAttestation.from_dict({
        "attestation_version": 1,
        "status": "not_required",
    })
    assert restored is not None
    assert not restored.valid(None, None, 0, {}, build_task_identity("x", "c", 1))


def test_new_attestation_requires_task_identity_when_present():
    ledger, verification = _ready()
    identity = build_task_identity("edit app/a.py", "conv-1", 2)
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1}, identity)
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, None)


def main():
    tests = [
        ("task-bound attestation validates", test_task_bound_attestation_validates),
        ("different conversation cannot reuse attestation", test_different_conversation_cannot_reuse_attestation),
        ("different original task cannot reuse attestation", test_different_original_task_cannot_reuse_attestation),
        ("plan revision change invalidates attestation", test_plan_revision_change_invalidates_attestation),
        ("legacy Setup 4.45 attestation restores safely", test_legacy_setup_445_attestation_restores_safely),
        ("new attestation requires task identity when present", test_new_attestation_requires_task_identity_when_present),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.46 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test()
            print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            raise SystemExit(1)
    print("\nSetup 4.46 tests complete.")

if __name__ == "__main__":
    main()
