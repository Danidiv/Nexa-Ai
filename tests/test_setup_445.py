"""Setup 4.45 completion attestation tests."""
from services.completion_attestation import CompletionAttestation, create_attestation
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.impact_verification import ImpactVerification


def _ready():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("write_file", "modification", "app/a.py", {"ok": True}, 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app/a.py", {"ok": True}, 1, 1))
    verification = ImpactVerification(["app/a.py"], ["app/a.py"], [], "complete", "verified")
    ledger.evaluate(verification, True, 1, {"app/a.py": 1})
    return ledger, verification


def test_attestation_seals_sufficient_completion():
    ledger, verification = _ready()
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1})
    assert att.status == "sealed"
    assert att.valid(ledger, verification, 1, {"app/a.py": 1})


def test_attestation_detects_tampered_evidence_checkpoint():
    ledger, verification = _ready()
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1})
    ledger.entries[-1]["fingerprint"] = "tampered"
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1})


def test_new_evidence_invalidates_attestation():
    ledger, verification = _ready()
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1})
    ledger.add(make_evidence("read_file", "verification", "app/a.py", {"ok": True}, 1, 1))
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1})


def test_resource_generation_change_invalidates_attestation():
    ledger, verification = _ready()
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1})
    assert not att.valid(ledger, verification, 2, {"app/a.py": 2})


def test_legacy_state_without_attestation_is_safe():
    restored = CompletionAttestation.from_dict({"attestation_version": 1, "status": "not_required"})
    assert restored is not None
    assert not restored.valid(None, None, 0, {})


def test_independent_generation_does_not_match_wrong_attestation():
    ledger, verification = _ready()
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1})
    assert att.valid(ledger, verification, 1, {"app/a.py": 1})
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1, "app/b.py": 2})


def main():
    tests = [
        ("attestation seals sufficient completion", test_attestation_seals_sufficient_completion),
        ("tampered evidence checkpoint invalidates attestation", test_attestation_detects_tampered_evidence_checkpoint),
        ("new evidence invalidates prior attestation", test_new_evidence_invalidates_attestation),
        ("resource generation changes invalidate attestation", test_resource_generation_change_invalidates_attestation),
        ("legacy state without attestation restores safely", test_legacy_state_without_attestation_is_safe),
        ("independent generations cannot reuse a mismatched attestation", test_independent_generation_does_not_match_wrong_attestation),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.45 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test()
            print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            raise SystemExit(1)
    print("\nSetup 4.45 tests complete.")

if __name__ == "__main__":
    main()
