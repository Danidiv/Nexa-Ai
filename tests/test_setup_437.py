"""Setup 4.37 tests: evidence-based completion."""
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.impact_verification import build_impact_verification
from core.agent.agent_loop import AgentState, _safe_state_snapshot, _restore_state_snapshot


def change_plan():
    return {
        "verify_paths": ["app.js", "index.html"],
        "targets": ["app.js"],
        "dependent_paths": ["index.html"],
    }


def test_successful_modification_is_recorded_as_evidence():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "SUCCESS: edited"))
    assert len(ledger.entries) == 1
    assert ledger.entries[0]["category"] == "modification"
    assert ledger.entries[0]["fingerprint"]
    print("[PASS] successful modification produces compact execution evidence")


def test_completion_requires_verification_evidence_for_each_required_path():
    verification = build_impact_verification(change_plan(), {"app.js"}, {"app.js", "index.html"})
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "SUCCESS"))
    ledger.add(make_evidence("read_file", "verification", "app.js", "SUCCESS"))
    ledger.evaluate(verification, True)
    assert ledger.status == "insufficient"
    assert "verification evidence for index.html" in ledger.missing_requirements
    print("[PASS] completion is blocked when an impact path lacks evidence")


def test_complete_evidence_requires_modification_and_all_verification_paths():
    verification = build_impact_verification(change_plan(), {"app.js"}, {"app.js", "index.html"})
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "SUCCESS"))
    ledger.add(make_evidence("read_file", "verification", "app.js", "SUCCESS"))
    ledger.add(make_evidence("read_file", "verification", "index.html", "SUCCESS"))
    ledger.evaluate(verification, True)
    assert ledger.status == "sufficient"
    assert ledger.missing_requirements == []
    print("[PASS] completion becomes sufficient only with complete verification evidence")


def test_non_modified_tasks_do_not_require_completion_evidence():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.evaluate(None, False)
    assert ledger.status == "not_required"
    print("[PASS] informational/non-modifying tasks remain free of evidence gating")


def test_evidence_is_json_safe_and_restores():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("read_file", "verification", "shop/app.js", {"ok": True}))
    restored = CompletionEvidenceLedger.from_dict(ledger.to_dict())
    assert restored is not None
    assert restored.to_dict() == ledger.to_dict()
    print("[PASS] completion evidence serializes and restores as JSON-safe state")


def test_evidence_is_bounded():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    for i in range(100):
        ledger.add(make_evidence("read_file", "verification", f"f{i}.js", "ok"))
    assert len(ledger.entries) <= 32
    print("[PASS] completion evidence remains bounded")


def test_agent_state_persists_completion_evidence():
    state = AgentState()
    state.verification_requested = True
    state.modified_resources = {"app.js"}
    state.observed_resources = {"app.js", "index.html"}
    state.impact_verification = build_impact_verification(change_plan(), state.modified_resources, state.observed_resources)
    state.completion_evidence.add(make_evidence("edit_file", "modification", "app.js", "SUCCESS"))
    state.completion_evidence.add(make_evidence("read_file", "verification", "app.js", "SUCCESS"))
    state.completion_evidence.add(make_evidence("read_file", "verification", "index.html", "SUCCESS"))
    state.completion_evidence.evaluate(state.impact_verification, True)
    snapshot = _safe_state_snapshot(state)
    restored = AgentState()
    _restore_state_snapshot(restored, snapshot)
    assert restored.completion_evidence is not None
    assert restored.completion_evidence.status == "sufficient"
    assert len(restored.completion_evidence.entries) == 3
    print("[PASS] agent state restores evidence-based completion checkpoint safely")


if __name__ == "__main__":
    print("=" * 60)
    print("AZIZ AI SETUP 4.37 TEST")
    print("=" * 60)
    for name in (
        "test_successful_modification_is_recorded_as_evidence",
        "test_completion_requires_verification_evidence_for_each_required_path",
        "test_complete_evidence_requires_modification_and_all_verification_paths",
        "test_non_modified_tasks_do_not_require_completion_evidence",
        "test_evidence_is_json_safe_and_restores",
        "test_evidence_is_bounded",
        "test_agent_state_persists_completion_evidence",
    ):
        globals()[name]()
    print("\nSetup 4.37 tests complete.")
