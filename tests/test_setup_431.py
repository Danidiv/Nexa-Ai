"""Setup 4.31 - task decomposition and planning intelligence."""
from services.task_decomposer import TaskDecomposer
from core.agent.agent_loop import AgentSession, AgentState, _safe_state_snapshot, _restore_state_snapshot


def main():
    print("=" * 60)
    print("AZIZ AI SETUP 4.31 TEST")
    print("=" * 60)

    d = TaskDecomposer()
    plan = d.decompose("Build an e-commerce website with login, shopping cart and database, then run tests")
    titles = [s.title for s in plan.steps]
    assert titles[0] == "Inspect context"
    assert "Implement structure" in titles
    assert "Implement features" in titles
    assert "Run verification" in titles
    assert "Repair if needed" in titles
    assert titles[-1] == "Complete"
    for i, step in enumerate(plan.steps[1:], 1):
        assert step.depends_on == [plan.steps[i - 1].id]
    print("[PASS] complex coding requests decompose into meaningful dependent subtasks")

    plan.mark_completed("S1")
    assert plan.next_step().id == "S2"
    assert all(s.status == "pending" for s in plan.steps[2:])
    print("[PASS] decomposition preserves ordered execution checkpoints")

    question = d.decompose("What is a local AI coding agent?")
    assert question.steps and all("without modifying project resources" in s.objective.lower() or "question" in s.objective.lower() for s in question.steps)
    print("[PASS] informational requests remain non-destructive")

    session = AgentSession()
    session.start_task("Create a dashboard with login and run tests")
    assert session.state.plan is not None
    assert session.state.plan.steps[0].title == "Inspect context"
    assert any("SETUP 4.31 TASK DECOMPOSITION PLAN" in m.get("content", "") for m in session.messages)
    print("[PASS] new sessions use the decomposed task plan")

    snapshot = _safe_state_snapshot(session.state)
    restored = AgentState()
    _restore_state_snapshot(restored, snapshot)
    assert restored.plan is not None
    assert [s.title for s in restored.plan.steps] == [s.title for s in session.state.plan.steps]
    print("[PASS] decomposed plans persist and restore safely")

    simple = d.decompose("Fix app.js and run the build")
    assert len(simple.steps) >= 5
    assert any("app.js" in s.objective for s in simple.steps)
    print("[PASS] file-specific repair tasks retain referenced context")

    print("\nSetup 4.31 tests complete.")


if __name__ == "__main__":
    main()
