"""Setup 4.41 tests: evidence provenance and ordering integrity."""
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.impact_verification import build_impact_verification


def test_verification_links_to_latest_resource_modification():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A", 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app.js", "verified", 1, 1))
    item = ledger.entries[-1]
    assert item["sequence"] == 2
    assert item["parent_evidence_id"] == ledger.entries[-2]["evidence_id"]
    assert ledger.provenance_valid(["app.js"])
    print("[PASS] verification evidence links to the latest modification")


def test_new_modification_gets_new_verification_parent():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A", 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app.js", "verified-1", 1, 1))
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A2", 2, 2))
    ledger.add(make_evidence("read_file", "verification", "app.js", "verified-2", 2, 2))
    assert ledger.entries[-1]["parent_evidence_id"] == ledger.entries[-2]["evidence_id"]
    assert ledger.entries[-1]["sequence"] > ledger.entries[-2]["sequence"]
    print("[PASS] repeated modification creates a new verification lineage")


def test_invalid_parent_chain_blocks_completion():
    verification = build_impact_verification({"verify_paths": ["app.js"]}, {"app.js"}, {"app.js"})
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A", 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app.js", "verified", 1, 1))
    ledger.entries[-1]["parent_evidence_id"] = "missing-parent"
    ledger.evaluate(verification, True, 1, {"app.js": 1})
    assert ledger.status == "insufficient"
    assert "valid evidence provenance chain" in ledger.missing_requirements
    print("[PASS] broken provenance chain blocks completion")


def test_sequence_order_is_enforced():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A", 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app.js", "verified", 1, 1))
    ledger.entries[1]["sequence"] = ledger.entries[0]["sequence"]
    assert not ledger.provenance_valid(["app.js"])
    print("[PASS] non-monotonic evidence sequence is rejected")


def test_legacy_v2_evidence_restores():
    data = {
        "evidence_version": 2,
        "entries": [{
            "evidence_version": 2, "evidence_id": "e1", "action": "edit_file",
            "category": "modification", "path": "app.js", "outcome": "success",
            "fingerprint": "abc", "change_epoch": 1, "resource_epoch": 1,
        }],
        "status": "insufficient", "missing_requirements": [],
    }
    restored = CompletionEvidenceLedger.from_dict(data)
    assert restored is not None
    assert restored.entries[0]["sequence"] == 0
    print("[PASS] legacy Setup 4.40 evidence restores safely")


def test_unrelated_resource_lineage_remains_valid():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A", 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app.js", "A-ok", 1, 1))
    ledger.add(make_evidence("edit_file", "modification", "cart.js", "B", 2, 2))
    ledger.add(make_evidence("read_file", "verification", "cart.js", "B-ok", 2, 2))
    assert ledger.provenance_valid(["app.js", "cart.js"])
    print("[PASS] independent resource evidence chains remain valid")


if __name__ == "__main__":
    print("=" * 60)
    print("AZIZ AI SETUP 4.41 TEST")
    print("=" * 60)
    for name in (
        "test_verification_links_to_latest_resource_modification",
        "test_new_modification_gets_new_verification_parent",
        "test_invalid_parent_chain_blocks_completion",
        "test_sequence_order_is_enforced",
        "test_legacy_v2_evidence_restores",
        "test_unrelated_resource_lineage_remains_valid",
    ):
        globals()[name]()
    print("\nSetup 4.41 tests complete.")
