"""Setup 4.36 tests: change-impact verification."""
from services.impact_verification import ImpactVerification, build_impact_verification
from core.agent.agent_loop import AgentState


def change_plan():
    return {
        "change_plan_version": 1,
        "targets": ["app.js"],
        "inspect_paths": ["cart.js", "app.js", "index.html"],
        "change_paths": ["app.js"],
        "verify_paths": ["app.js", "index.html"],
        "dependency_paths": ["cart.js"],
        "dependent_paths": ["index.html"],
        "rationale": [],
    }


def test_initial_scope_requires_target_and_dependents():
    result = build_impact_verification(change_plan(), {"app.js"}, set())
    assert result.status == "pending"
    assert result.required_paths == ["app.js", "index.html"]
    assert result.missing_paths == ["app.js", "index.html"]
    print("[PASS] verification scope includes changed targets and affected dependents")


def test_target_read_only_is_partial_until_dependents_verified():
    result = build_impact_verification(change_plan(), {"app.js"}, {"app.js"})
    assert result.status == "partial"
    assert result.completed_paths == ["app.js"]
    assert result.missing_paths == ["index.html"]
    print("[PASS] target verification remains incomplete while a dependent is unverified")


def test_all_required_paths_complete():
    result = build_impact_verification(change_plan(), {"app.js"}, {"app.js", "index.html"})
    assert result.status == "complete"
    assert result.missing_paths == []
    assert result.summary().startswith("Change-impact verification complete")
    print("[PASS] verification completes only after every required impact path is observed")


def test_observed_paths_match_project_relative_variants():
    result = build_impact_verification(change_plan(), {"shop-app/app.js"}, {"shop-app/app.js", "shop-app/index.html"})
    assert result.status == "complete"
    print("[PASS] verification safely matches relative project path variants")


def test_no_change_plan_falls_back_to_modified_resources():
    result = build_impact_verification(None, {"test.txt"}, set())
    assert result.required_paths == ["test.txt"]
    assert result.status == "pending"
    result = build_impact_verification(None, {"test.txt"}, {"test.txt"})
    assert result.status == "complete"
    print("[PASS] missing impact plans still enforce read-after-change verification")


def test_verification_serializes_and_restores():
    result = build_impact_verification(change_plan(), {"app.js"}, {"app.js"})
    restored = ImpactVerification.from_dict(result.to_dict())
    assert restored is not None
    assert restored.to_dict() == result.to_dict()
    print("[PASS] impact verification persists as JSON-safe state")


def test_agent_state_persists_verification_and_resource_observations():
    state = AgentState()
    state.verification_requested = True
    state.modified_resources = {"app.js"}
    state.observed_resources = {"app.js"}
    state.impact_verification = build_impact_verification(change_plan(), state.modified_resources, state.observed_resources)
    from core.agent.agent_loop import _safe_state_snapshot, _restore_state_snapshot
    snapshot = _safe_state_snapshot(state)
    restored = AgentState()
    _restore_state_snapshot(restored, snapshot)
    assert restored.impact_verification is not None
    assert restored.impact_verification.status == "partial"
    assert restored.modified_resources == {"app.js"}
    assert restored.observed_resources == {"app.js"}
    print("[PASS] agent state restores the impact verification checkpoint safely")


if __name__ == "__main__":
    print("=" * 60)
    print("AZIZ AI SETUP 4.36 TEST")
    print("=" * 60)
    for name in (
        "test_initial_scope_requires_target_and_dependents",
        "test_target_read_only_is_partial_until_dependents_verified",
        "test_all_required_paths_complete",
        "test_observed_paths_match_project_relative_variants",
        "test_no_change_plan_falls_back_to_modified_resources",
        "test_verification_serializes_and_restores",
        "test_agent_state_persists_verification_and_resource_observations",
    ):
        globals()[name]()
    print("\nSetup 4.36 tests complete.")
