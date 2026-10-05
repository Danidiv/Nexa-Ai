"""Setup 4.44 audit checkpoint tests."""
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.impact_verification import ImpactVerification


def _ready():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("write_file", "modification", "app/a.py", {"ok": True}, 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app/a.py", {"ok": True}, 1, 1))
    verification = ImpactVerification(
        required_paths=["app/a.py"],
        completed_paths=["app/a.py"],
        missing_paths=[],
        status="complete",
        rationale="verified",
    )
    ledger.evaluate(verification, True, 1, {"app/a.py": 1})
    return ledger, verification


def test_checkpoint_created_and_valid():
    ledger, _ = _ready()
    assert ledger.checkpoint_hash
    assert ledger.checkpoint_valid()


def test_tampered_checkpointed_evidence_is_detected():
    ledger, _ = _ready()
    ledger.entries[-1]["fingerprint"] = "tampered"
    assert not ledger.checkpoint_valid()


def test_new_evidence_invalidates_old_checkpoint():
    ledger, _ = _ready()
    old = ledger.checkpoint_hash
    ledger.add(make_evidence("read_file", "verification", "app/a.py", {"ok": True}, 1, 1))
    assert old
    assert not ledger.checkpoint_hash


def test_checkpoint_rollover_survives_bounded_ledger():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    for i in range(40):
        ledger.add(make_evidence("read_file", "verification", f"app/{i}.py", i + 1, i + 1, i + 1))
    ledger.status = "sufficient"
    ledger.missing_requirements = []
    ledger.create_checkpoint()
    assert len(ledger.entries) == 32
    assert ledger.checkpoint_valid()
    assert ledger.integrity_valid()


def test_legacy_setup_443_restores_without_checkpoint():
    ledger, _ = _ready()
    data = ledger.to_dict()
    data.pop("checkpoint_version", None)
    data.pop("checkpoint_hash", None)
    data.pop("checkpoint_sequence", None)
    data.pop("checkpoint_head_hash", None)
    restored = CompletionEvidenceLedger.from_dict(data)
    assert restored is not None
    assert restored.checkpoint_hash == ""
    assert restored.identity_valid()


def test_checkpoint_changes_when_audit_state_changes():
    ledger, _ = _ready()
    first = ledger.checkpoint_hash
    ledger.status = "insufficient"
    ledger.missing_requirements = ["test"]
    ledger.create_checkpoint()
    assert ledger.checkpoint_hash != first
    assert ledger.checkpoint_valid()


def main():
    tests = [
        ("audit checkpoint is created and valid", test_checkpoint_created_and_valid),
        ("tampered checkpointed evidence is detected", test_tampered_checkpointed_evidence_is_detected),
        ("new evidence invalidates the old checkpoint", test_new_evidence_invalidates_old_checkpoint),
        ("bounded ledger rollover preserves checkpoint integrity", test_checkpoint_rollover_survives_bounded_ledger),
        ("legacy Setup 4.43 evidence restores without a checkpoint", test_legacy_setup_443_restores_without_checkpoint),
        ("checkpoint changes when audit state changes", test_checkpoint_changes_when_audit_state_changes),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.44 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test()
            print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            raise SystemExit(1)
    print("\nSetup 4.44 tests complete.")


if __name__ == "__main__":
    main()
