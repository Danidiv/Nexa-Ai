"""Setup 4.47 capability-bound completion attestation tests."""
from services.completion_attestation import (
    CompletionAttestation,
    build_task_identity,
    capability_identity_digest,
    create_attestation,
)
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.impact_verification import ImpactVerification

CAPS = [
    {"name": "write_file", "arguments": [{"name": "path", "required": True, "type": "string"}]},
    {"name": "read_file", "arguments": [{"name": "path", "required": True, "type": "string"}]},
]


def _ready():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("write_file", "modification", "app/a.py", {"ok": True}, 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app/a.py", {"ok": True}, 1, 1))
    verification = ImpactVerification(["app/a.py"], ["app/a.py"], [], "complete", "verified")
    ledger.evaluate(verification, True, 1, {"app/a.py": 1})
    return ledger, verification


def _identity():
    return build_task_identity("edit app/a.py", "conv-1", 2)


def test_capability_bound_attestation_validates():
    ledger, verification = _ready()
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1}, _identity(), CAPS)
    assert att.status == "sealed"
    assert att.capability_digest == capability_identity_digest(CAPS)
    assert att.valid(ledger, verification, 1, {"app/a.py": 1}, _identity(), CAPS)


def test_changed_capabilities_invalidate_attestation():
    ledger, verification = _ready()
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1}, _identity(), CAPS)
    changed = [*CAPS, {"name": "run_python", "arguments": []}]
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, _identity(), changed)


def test_capability_order_is_deterministic():
    reversed_caps = list(reversed(CAPS))
    assert capability_identity_digest(CAPS) == capability_identity_digest(reversed_caps)
    assert capability_identity_digest(CAPS) == capability_identity_digest([
        {"name": "write_file", "arguments": [{"type": "string", "required": True, "name": "path"}]},
        {"name": "read_file", "arguments": [{"name": "path", "type": "string", "required": True}]},
    ])


def test_legacy_setup_446_attestation_restores_safely():
    restored = CompletionAttestation.from_dict({"attestation_version": 2, "status": "not_required"})
    assert restored is not None
    assert restored.capability_digest == ""
    assert not restored.valid(None, None, 0, {}, _identity(), CAPS)


def test_capability_digest_is_bounded_and_stable():
    digest = capability_identity_digest(CAPS)
    assert len(digest) == 24
    assert capability_identity_digest(CAPS) == digest
    assert capability_identity_digest([]) == ""


def test_missing_capability_identity_cannot_reuse_new_attestation():
    ledger, verification = _ready()
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1}, _identity(), CAPS)
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, _identity(), None)


def main():
    tests = [
        ("capability-bound attestation validates", test_capability_bound_attestation_validates),
        ("changed capabilities invalidate attestation", test_changed_capabilities_invalidate_attestation),
        ("capability order is deterministic", test_capability_order_is_deterministic),
        ("legacy Setup 4.46 attestation restores safely", test_legacy_setup_446_attestation_restores_safely),
        ("capability digest is bounded and stable", test_capability_digest_is_bounded_and_stable),
        ("missing capability identity cannot reuse new attestation", test_missing_capability_identity_cannot_reuse_new_attestation),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.47 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test()
            print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            raise SystemExit(1)
    print("\nSetup 4.47 tests complete.")


if __name__ == "__main__":
    main()
