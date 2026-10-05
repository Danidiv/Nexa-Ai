"""Setup 4.48 runtime-bound completion attestation tests."""
from services.completion_attestation import (
    CompletionAttestation,
    build_runtime_identity,
    build_task_identity,
    create_attestation,
    runtime_identity_digest,
)
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.impact_verification import ImpactVerification

RUNTIME = {"backend": "LMStudioGateway", "model": "qwen/qwen3.5-9b", "endpoint": "http://localhost:1234/v1"}
CAPS = [{"name": "write_file", "arguments": [{"name": "path", "required": True, "type": "string"}]}]


def _ready():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("write_file", "modification", "app/a.py", {"ok": True}, 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app/a.py", {"ok": True}, 1, 1))
    verification = ImpactVerification(["app/a.py"], ["app/a.py"], [], "complete", "verified")
    ledger.evaluate(verification, True, 1, {"app/a.py": 1})
    return ledger, verification


def _identity():
    return build_task_identity("edit app/a.py", "conv-1", 2)


def _att():
    ledger, verification = _ready()
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1}, _identity(), CAPS, RUNTIME)
    return ledger, verification, att


def test_runtime_bound_attestation_validates():
    ledger, verification, att = _att()
    assert att.status == "sealed"
    assert att.runtime_digest == runtime_identity_digest(RUNTIME)
    assert att.valid(ledger, verification, 1, {"app/a.py": 1}, _identity(), CAPS, RUNTIME)


def test_changed_runtime_invalidates_attestation():
    ledger, verification, att = _att()
    changed = {**RUNTIME, "model": "different-model"}
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, _identity(), CAPS, changed)


def test_runtime_identity_order_is_deterministic():
    a = {"backend": "LMStudioGateway", "model": "qwen/qwen3.5-9b", "endpoint": "http://localhost:1234/v1"}
    b = {"endpoint": "http://localhost:1234/v1", "model": "qwen/qwen3.5-9b", "backend": "LMStudioGateway"}
    assert runtime_identity_digest(a) == runtime_identity_digest(b)
    assert len(runtime_identity_digest(a)) == 24


def test_legacy_setup_447_attestation_restores_safely():
    restored = CompletionAttestation.from_dict({"attestation_version": 3, "status": "not_required"})
    assert restored is not None
    assert restored.runtime_digest == ""
    assert not restored.valid(None, None, 0, {}, _identity(), CAPS, RUNTIME)


def test_runtime_digest_excludes_transient_state_and_secrets():
    base = dict(RUNTIME)
    noisy = {**RUNTIME, "health": "healthy", "api_key": "SECRET", "request_count": "99"}
    assert runtime_identity_digest(base) == runtime_identity_digest(noisy)
    assert len(runtime_identity_digest(base)) == 24


def test_missing_runtime_identity_cannot_reuse_new_attestation():
    ledger, verification, att = _att()
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, _identity(), CAPS, None)


def main():
    tests = [
        ("runtime-bound attestation validates", test_runtime_bound_attestation_validates),
        ("changed runtime invalidates attestation", test_changed_runtime_invalidates_attestation),
        ("runtime identity order is deterministic", test_runtime_identity_order_is_deterministic),
        ("legacy Setup 4.47 attestation restores safely", test_legacy_setup_447_attestation_restores_safely),
        ("runtime digest detects state changes", test_runtime_digest_excludes_transient_state_and_secrets),
        ("missing runtime identity cannot reuse new attestation", test_missing_runtime_identity_cannot_reuse_new_attestation),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.48 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test()
            print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            raise SystemExit(1)
    print("\nSetup 4.48 tests complete.")


if __name__ == "__main__":
    main()
