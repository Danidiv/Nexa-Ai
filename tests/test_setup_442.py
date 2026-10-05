"""Setup 4.42 tests: tamper-evident evidence integrity chain."""
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.impact_verification import build_impact_verification


def test_hash_chain_is_created_and_valid():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A", 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app.js", "verified", 1, 1))
    assert ledger.entries[0]["chain_hash"]
    assert ledger.entries[1]["chain_hash"]
    assert ledger.integrity_valid()
    print("[PASS] evidence entries form a valid integrity hash chain")


def test_tampered_evidence_is_detected():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A", 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app.js", "verified", 1, 1))
    ledger.entries[0]["fingerprint"] = "tampered"
    assert not ledger.integrity_valid()
    print("[PASS] tampered evidence is detected")


def test_tampered_chain_blocks_completion():
    verification = build_impact_verification({"verify_paths": ["app.js"]}, {"app.js"}, {"app.js"})
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A", 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app.js", "verified", 1, 1))
    ledger.entries[1]["chain_hash"] = "broken-chain"
    ledger.evaluate(verification, True, 1, {"app.js": 1})
    assert ledger.status == "insufficient"
    assert "valid evidence integrity chain" in ledger.missing_requirements
    print("[PASS] broken integrity chain blocks completion")


def test_independent_changes_extend_one_valid_chain():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A", 1, 1))
    first = ledger.entries[-1]["chain_hash"]
    ledger.add(make_evidence("edit_file", "modification", "cart.js", "B", 2, 2))
    assert ledger.integrity_valid()
    assert ledger.entries[-1]["chain_hash"] != first
    print("[PASS] independent resources remain valid while sharing the audit chain")


def test_legacy_setup_441_evidence_restores():
    data = {
        "evidence_version": 3,
        "entries": [{
            "evidence_version": 3, "evidence_id": "e1", "action": "edit_file",
            "category": "modification", "path": "app.js", "outcome": "success",
            "fingerprint": "abc", "change_epoch": 1, "resource_epoch": 1,
            "sequence": 1, "parent_evidence_id": "",
        }],
        "status": "insufficient", "missing_requirements": [],
    }
    restored = CompletionEvidenceLedger.from_dict(data)
    assert restored is not None
    assert restored.entries[0]["chain_hash"] == ""
    assert restored.integrity_valid()
    print("[PASS] legacy Setup 4.41 evidence restores safely")


def test_bounded_ledger_preserves_integrity_after_rollover():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    for i in range(40):
        ledger.add(make_evidence("edit_file", "modification", f"file{i}.js", str(i), i + 1, i + 1))
    assert len(ledger.entries) == 32
    assert ledger.chain_anchor
    assert ledger.integrity_valid()
    print("[PASS] bounded ledger preserves integrity after evidence rollover")


if __name__ == "__main__":
    print("=" * 60)
    print("AZIZ AI SETUP 4.42 TEST")
    print("=" * 60)
    for name in (
        "test_hash_chain_is_created_and_valid",
        "test_tampered_evidence_is_detected",
        "test_tampered_chain_blocks_completion",
        "test_independent_changes_extend_one_valid_chain",
        "test_legacy_setup_441_evidence_restores",
        "test_bounded_ledger_preserves_integrity_after_rollover",
    ):
        globals()[name]()
    print("\nSetup 4.42 tests complete.")
