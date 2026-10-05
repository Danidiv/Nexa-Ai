import json

from core.agent.agent_loop import AgentState, _restore_state_snapshot, _safe_state_snapshot


def test_setup_412():
    print("=" * 60)
    print("AZIZ AI SETUP 4.12 TEST")
    print("=" * 60)

    state = AgentState()
    state.phase = "VERIFY"
    state.step = 7
    state.successful_actions = ["write_file:path=a"]
    state.failed_actions = ["bad_action"]
    state.last_action = "read_file:path=a"
    state.last_result = "hello"
    state.verification_requested = True
    state.modified_resources = {"a.txt"}
    state.observed_resources = {"a.txt", "b.txt"}

    snapshot = _safe_state_snapshot(state)
    json.dumps(snapshot)
    print("[PASS] agent state snapshot is JSON serializable")

    restored = AgentState()
    _restore_state_snapshot(restored, snapshot)

    assert restored.phase == "VERIFY"
    assert restored.step == 7
    assert restored.successful_actions == ["write_file:path=a"]
    assert restored.failed_actions == ["bad_action"]
    assert restored.last_action == "read_file:path=a"
    assert restored.last_result == "hello"
    assert restored.verification_requested is True
    assert restored.modified_resources == {"a.txt"}
    assert restored.observed_resources == {"a.txt", "b.txt"}
    print("[PASS] agent state restores correctly")

    print("\nSetup 4.12 tests complete.")


if __name__ == "__main__":
    test_setup_412()
