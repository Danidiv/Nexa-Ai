"""AZIZ AI SETUP 4.30 TEST - structured task planning."""
import json
from services.task_planner import TaskPlan, TaskPlanner
from core.agent.agent_loop import AgentState, AgentSession, _safe_state_snapshot, _restore_state_snapshot


def main():
    print("=" * 60)
    print("AZIZ AI SETUP 4.30 TEST")
    print("=" * 60)

    planner = TaskPlanner()
    plan = planner.create_plan("Fix my_website/index.html and run the build")
    assert len(plan.steps) == 4
    assert plan.steps[0].id == "S1"
    assert plan.steps[1].depends_on == ["S1"]
    assert plan.next_step().id == "S1"
    print("[PASS] planner creates ordered steps with dependencies")

    plan.mark_completed("S1")
    assert plan.next_step().id == "S2"
    plan.mark_completed("S2")
    assert plan.next_step().id == "S3"
    print("[PASS] planner advances only when dependencies are complete")

    restored = TaskPlan.from_dict(plan.to_dict())
    assert restored is not None
    assert restored.summary() == plan.summary()
    assert json.loads(json.dumps(restored.to_dict(), ensure_ascii=False))["plan_version"] == 1
    print("[PASS] plan serializes and restores as JSON-safe state")

    state = AgentState()
    state.plan = planner.create_plan("Create a test file")
    state.current_plan_step = state.plan.next_step().id
    snapshot = _safe_state_snapshot(state)
    assert snapshot["plan"]["plan_version"] == 1
    restored_state = AgentState()
    _restore_state_snapshot(restored_state, snapshot)
    assert restored_state.plan is not None
    assert restored_state.current_plan_step == "S1"
    print("[PASS] agent state persists and restores the execution plan")

    state.record_action("read_file", {"path": "test.txt"}, "SUCCESS: content")
    assert state.plan.steps[0].status == "completed"
    assert state.current_plan_step == "S2"
    print("[PASS] successful actions advance the advisory plan")

    session = AgentSession()
    session.start_task("Create a landing page and run the build")
    assert session.state.plan is not None
    assert any("SETUP 4.30 EXECUTION PLAN" in m.get("content", "") for m in session.messages)
    print("[PASS] new agent sessions expose the execution plan to the model")

    question_plan = planner.create_plan("What is an AI coding agent?")
    assert [s.id for s in question_plan.steps] == ["S1", "S2"]
    assert "Answer" in question_plan.steps[0].objective
    print("[PASS] informational tasks get a non-destructive answer plan")

    print("\nSetup 4.30 tests complete.")


if __name__ == "__main__":
    main()
