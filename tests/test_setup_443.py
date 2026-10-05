"""Setup 4.43 tests: evidence identity and replay protection."""
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.impact_verification import build_impact_verification


def test_repeated_identical_evidence_gets_unique_identity():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("read_file", "verification", "app.js", "same", 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app.js", "same", 1, 1))
    assert len({e["evidence_id"] for e in ledger.entries}) == 2
    assert ledger.identity_valid()
    assert ledger.integrity_valid()
    print("[PASS] repeated identical evidence receives unique identities")


def test_duplicate_identity_blocks_completion():
    verification = build_impact_verification({"verify_paths": ["app.js"]}, {"app.js"}, {"app.js"})
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A", 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app.js", "verified", 1, 1))
    ledger.entries[1]["evidence_id"] = ledger.entries[0]["evidence_id"]
    ledger.evaluate(verification, True, 1, {"app.js": 1})
    assert ledger.status == "insufficient"
    assert "valid evidence identity/replay state" in ledger.missing_requirements
    print("[PASS] duplicate evidence identity blocks completion")


def test_replay_identity_does_not_break_independent_resources():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A", 1, 1))
    ledger.add(make_evidence("edit_file", "modification", "cart.js", "A", 2, 2))
    assert ledger.identity_valid()
    assert ledger.integrity_valid()
    assert ledger.entries[0]["evidence_id"] != ledger.entries[1]["evidence_id"]
    print("[PASS] independent resources keep distinct evidence identities")


def test_sequence_order_and_identity_are_both_required():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A", 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app.js", "B", 1, 1))
    ledger.entries[1]["sequence"] = ledger.entries[0]["sequence"]
    assert not ledger.identity_valid()
    print("[PASS] non-monotonic sequence remains an identity violation")


def test_legacy_setup_442_restores_safely():
    data = {
        "evidence_version": 4,
        "entries": [{
            "evidence_version": 4, "evidence_id": "e1", "action": "edit_file",
            "category": "modification", "path": "app.js", "outcome": "success",
            "fingerprint": "abc", "change_epoch": 1, "resource_epoch": 1,
            "sequence": 1, "parent_evidence_id": "", "chain_hash": "hash",
        }],
        "status": "insufficient", "missing_requirements": [], "chain_anchor": "",
    }
    restored = CompletionEvidenceLedger.from_dict(data)
    assert restored is not None
    assert restored.identity_valid()
    print("[PASS] legacy Setup 4.42 evidence restores safely")


def test_bounded_rollover_keeps_unique_identity_state():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    for i in range(40):
        ledger.add(make_evidence("edit_file", "modification", f"file{i}.js", "same", i + 1, i + 1))
    assert len(ledger.entries) == 32
    assert ledger.identity_valid()
    assert ledger.integrity_valid()
    print("[PASS] bounded evidence rollover preserves identity integrity")


if __name__ == "__main__":
    print("=" * 60)
    print("AZIZ AI SETUP 4.43 TEST")
    print("=" * 60)
    for name in (
        "test_repeated_identical_evidence_gets_unique_identity",
        "test_duplicate_identity_blocks_completion",
        "test_replay_identity_does_not_break_independent_resources",
        "test_sequence_order_and_identity_are_both_required",
        "test_legacy_setup_442_restores_safely",
        "test_bounded_rollover_keeps_unique_identity_state",
    ):
        globals()[name]()
    print("\nSetup 4.43 tests complete.")
