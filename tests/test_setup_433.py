"""Setup 4.33 - context-aware planning."""
from pathlib import Path
from tempfile import TemporaryDirectory

from services.task_context import TaskContext, build_task_context
from services.task_decomposer import TaskDecomposer
from services.task_planner import TaskPlan
from core.agent.agent_loop import AgentState, _safe_state_snapshot, _restore_state_snapshot


def main():
    print("=" * 60)
    print("AZIZ AI SETUP 4.33 TEST")
    print("=" * 60)

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        workspace = root / "workspace"
        projects = root / "projects"
        workspace.mkdir()
        (workspace / "app.js").write_text("placeholder", encoding="utf-8")
        (projects / "shop-app").mkdir(parents=True)
        (projects / "shop-app" / "index.html").write_text("placeholder", encoding="utf-8")

        context = build_task_context(
            "Fix app.js in project shop-app",
            str(workspace),
            str(projects),
        )
        assert context.workspace_exists
        assert "shop-app" in context.project_names
        assert context.referenced_paths["app.js"] is True
        assert "index.html" in context.project_paths["shop-app"]
        print("[PASS] safe context discovery indexes existing workspace/project metadata")

        decomposer = TaskDecomposer()
        plan = decomposer.decompose("Fix app.js in project shop-app", context=context)
        assert plan.context is context
        assert "shop-app" in plan.steps[0].objective
        assert "app.js" in plan.steps[0].objective
        print("[PASS] decomposed plans use observed local context hints")

        missing = decomposer.decompose("Fix missing.js in project shop-app", context=context)
        assert "not currently visible" in missing.steps[0].objective
        print("[PASS] missing referenced paths remain explicit and non-assumptive")

        encoded = plan.to_dict()
        restored = TaskPlan.from_dict(encoded)
        assert restored is not None
        assert restored.context is not None
        assert "shop-app" in restored.context.project_names
        print("[PASS] context-aware plans serialize and restore safely")

        state = AgentState()
        state.plan = plan
        state.current_plan_step = "S1"
        plan.bind_current_step("S1")
        snapshot = _safe_state_snapshot(state)
        state2 = AgentState()
        _restore_state_snapshot(state2, snapshot)
        assert state2.plan.context is not None
        assert state2.plan.context.referenced_paths["app.js"] is True
        print("[PASS] persisted agent state retains planning context")

        # Informational work must not turn local metadata into a reason to edit.
        info = decomposer.decompose("What is the best way to fix app.js?", context=context)
        assert len(info.steps) == 3
        assert [step.title for step in info.steps] == ["Understand request", "Answer", "Verify answer"]
        print("[PASS] informational requests remain non-destructive with context")

        # Context is metadata-only; file contents must not be read by the indexer.
        assert context.workspace_paths == ["app.js"]
        assert context.project_paths["shop-app"] == ["index.html"]
        print("[PASS] context index remains metadata-only and bounded")

    print("\nSetup 4.33 tests complete.")


if __name__ == "__main__":
    main()
