"""Setup 4.32 - adaptive task replanning from observed results."""
from services.task_planner import TaskPlanner
from core.agent.agent_loop import AgentState, _safe_state_snapshot, _restore_state_snapshot


def main():
    print("=" * 60)
    print("AZIZ AI SETUP 4.32 TEST")
    print("=" * 60)

    planner = TaskPlanner()
    plan = planner.create_plan("Fix app.js and run the build")
    plan.bind_current_step("S1")
    # Advance to implementation checkpoint for the simulated failure.
    plan.mark_completed("S1")
    plan.bind_current_step("S2")
    repair = plan.adapt_after_result("edit_file", "ERROR: app.js has a syntax error")
    assert repair is not None
    assert repair.id.startswith("R")
    assert repair.title == "Diagnose verification failure"
    assert plan.steps[1].id == repair.id
    assert plan.steps[2].depends_on == [repair.id]
    assert plan.next_step().id == repair.id
    print("[PASS] observed failures insert an adaptive repair checkpoint")

    repair_result = plan.mark_completed(repair.id)
    assert repair_result
    assert plan.next_step().id == "S2"
    print("[PASS] completed repair unlocks the original pending task")

    # Duplicate failure must not grow the plan repeatedly.
    before = len(plan.steps)
    plan.bind_current_step("S2")
    same = plan.adapt_after_result("edit_file", "ERROR: app.js has a syntax error")
    assert same is not None
    assert len(plan.steps) == before
    print("[PASS] repeated failure does not create duplicate repair steps")

    missing = planner.create_plan("Fix missing config.json")
    missing.bind_current_step("S1")
    repair2 = missing.adapt_after_result("read_file", "ERROR: File not found: config.json")
    assert repair2.title == "Locate missing resource"
    print("[PASS] missing-resource failures choose targeted recovery work")

    state = AgentState()
    state.plan = planner.create_plan("Fix app.js and run tests")
    state.current_plan_step = "S1"
    state.plan.bind_current_step("S1")
    snapshot = _safe_state_snapshot(state)
    restored = AgentState()
    _restore_state_snapshot(restored, snapshot)
    assert restored.plan is not None
    assert restored.plan.revision == state.plan.revision
    print("[PASS] adaptive plan revision persists and restores safely")

    state.record_action("read_file", {"path": "app.js"}, "ERROR: File not found: app.js")
    assert state.current_plan_step and state.current_plan_step.startswith("R")
    assert state.plan.steps[0].status == "pending"
    print("[PASS] agent action failures trigger adaptive replanning")

    state.record_action("list_files", {}, "SUCCESS: app.js located")
    repair_ids = [s.id for s in state.plan.steps if s.id.startswith("R")]
    assert repair_ids and state.plan.steps[0].id == repair_ids[0]
    assert state.plan.steps[0].status == "completed"
    assert state.current_plan_step == "S1"
    print("[PASS] successful recovery action returns execution to the blocked task")

    print("\nSetup 4.32 tests complete.")


if __name__ == "__main__":
    main()
