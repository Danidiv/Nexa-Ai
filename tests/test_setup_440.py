"""Setup 4.40 tests: resource-scoped freshness for multi-file changes."""
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.impact_verification import build_impact_verification
from services.evidence_freshness import normalize_resource_key, resource_generation, is_resource_fresh
from core.agent.agent_loop import AgentState, _safe_state_snapshot, _restore_state_snapshot


def test_unrelated_modifications_do_not_invalidate_previous_resource_generation():
    verification = build_impact_verification({"verify_paths": ["app.js", "cart.js"]}, {"app.js", "cart.js"}, {"app.js", "cart.js"})
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A", 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app.js", "A-verified", 1, 1))
    ledger.add(make_evidence("edit_file", "modification", "cart.js", "B", 2, 2))
    ledger.add(make_evidence("read_file", "verification", "cart.js", "B-verified", 2, 2))
    ledger.evaluate(verification, True, 2, {"app.js": 1, "cart.js": 2})
    assert ledger.status == "sufficient"
    print("[PASS] unrelated resource changes preserve valid per-resource evidence")


def test_modified_resource_requires_its_latest_generation_evidence():
    verification = build_impact_verification({"verify_paths": ["app.js"]}, {"app.js"}, {"app.js"})
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A", 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app.js", "verified-1", 1, 1))
    ledger.add(make_evidence("edit_file", "modification", "app.js", "A2", 2, 2))
    ledger.evaluate(verification, True, 2, {"app.js": 2})
    assert ledger.status == "insufficient"
    assert any("verification evidence for app.js" in x for x in ledger.missing_requirements)
    print("[PASS] repeated modification invalidates only that resource's prior verification")


def test_resource_generation_helpers_are_safe():
    generations = {"project/app.js": 4}
    assert normalize_resource_key("./project\\app.js") == "project/app.js"
    assert resource_generation(generations, "project/app.js") == 4
    assert is_resource_fresh({"change_epoch": 4}, "project/app.js", generations)
    assert not is_resource_fresh({"change_epoch": 3}, "project/app.js", generations)
    print("[PASS] resource freshness helpers normalize and bound generations safely")


def test_state_persists_modified_generations():
    state = AgentState()
    state.change_epoch = 3
    state.modified_generations = {"app.js": 1, "cart.js": 3}
    snapshot = _safe_state_snapshot(state)
    restored = AgentState()
    _restore_state_snapshot(restored, snapshot)
    assert restored.modified_generations == {"app.js": 1, "cart.js": 3}
    print("[PASS] per-resource modification generations persist and restore")


def test_legacy_state_without_generations_restores_safely():
    state = AgentState()
    _restore_state_snapshot(state, {"change_epoch": 5})
    assert state.modified_generations == {}
    print("[PASS] legacy state without resource generations restores safely")


def test_informational_tasks_remain_unaffected():
    state = AgentState()
    state.completion_evidence.evaluate(None, False, state.change_epoch, state.modified_generations)
    assert state.completion_evidence.status == "not_required"
    print("[PASS] informational tasks remain outside resource freshness gating")


if __name__ == "__main__":
    print("=" * 60)
    print("AZIZ AI SETUP 4.40 TEST")
    print("=" * 60)
    for name in (
        "test_unrelated_modifications_do_not_invalidate_previous_resource_generation",
        "test_modified_resource_requires_its_latest_generation_evidence",
        "test_resource_generation_helpers_are_safe",
        "test_state_persists_modified_generations",
        "test_legacy_state_without_generations_restores_safely",
        "test_informational_tasks_remain_unaffected",
    ):
        globals()[name]()
    print("\nSetup 4.40 tests complete.")
