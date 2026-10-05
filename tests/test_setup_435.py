"""Setup 4.35 tests: dependency-aware change planning."""
from pathlib import Path
import tempfile

from services.change_planner import ChangePlan, build_change_plan
from services.task_context import build_task_context, TaskContext
from services.task_decomposer import TaskDecomposer


def make_project():
    root = Path(tempfile.mkdtemp())
    workspace = root / "workspace"
    projects = root / "projects"
    project = projects / "shop-app"
    project.mkdir(parents=True)
    workspace.mkdir()
    (project / "index.html").write_text('<script src="app.js"></script>', encoding="utf-8")
    (project / "app.js").write_text('import "./cart.js"; import "./styles.css";', encoding="utf-8")
    (project / "cart.js").write_text('export function total() { return 1; }', encoding="utf-8")
    (project / "styles.css").write_text('body { margin: 0; }', encoding="utf-8")
    return workspace, projects


def test_dependency_and_dependent_scope():
    workspace, projects = make_project()
    context = build_task_context("Fix app.js in project shop-app", str(workspace), str(projects))
    plan = build_change_plan(context)
    assert "app.js" in plan.targets
    assert "cart.js" in plan.dependency_paths
    assert "index.html" in plan.dependent_paths
    assert "cart.js" in plan.inspect_paths
    assert "index.html" in plan.verify_paths
    print("[PASS] dependency and dependent scope is derived from the relationship graph")


def test_change_scope_does_not_expand_to_all_related_files():
    workspace, projects = make_project()
    context = build_task_context("Fix app.js in project shop-app", str(workspace), str(projects))
    plan = build_change_plan(context)
    assert plan.change_paths == ["app.js"]
    assert "cart.js" not in plan.change_paths
    assert "index.html" not in plan.change_paths
    print("[PASS] related files remain inspect/verify scope instead of automatic edit scope")


def test_missing_target_is_non_assumptive():
    workspace, projects = make_project()
    context = build_task_context("Fix missing.js in project shop-app", str(workspace), str(projects))
    plan = build_change_plan(context)
    assert plan.targets == []
    assert plan.change_paths == []
    assert any("do not assume" in text.lower() or "no existing" in text.lower() for text in plan.rationale)
    print("[PASS] missing targets remain non-assumptive")


def test_change_plan_serializes_and_restores():
    workspace, projects = make_project()
    context = build_task_context("Fix app.js in project shop-app", str(workspace), str(projects))
    plan = build_change_plan(context)
    restored = ChangePlan.from_dict(plan.to_dict())
    assert restored is not None
    assert restored.to_dict() == plan.to_dict()
    print("[PASS] dependency-aware change plan serializes and restores safely")


def test_context_persists_change_plan():
    workspace, projects = make_project()
    context = build_task_context("Fix app.js in project shop-app", str(workspace), str(projects))
    restored = TaskContext.from_dict(context.to_dict())
    assert restored is not None
    assert restored.change_plan == context.change_plan
    print("[PASS] task context persists the dependency-aware change plan")


def test_decomposer_exposes_dependency_aware_hints():
    workspace, projects = make_project()
    context = build_task_context("Fix app.js in project shop-app", str(workspace), str(projects))
    plan = TaskDecomposer().decompose("Fix app.js in project shop-app", context=context)
    objective = plan.steps[0].objective
    assert "Primary change targets" in objective
    assert "Dependency-aware inspection scope" in objective
    assert "Dependency-aware verification scope" in objective
    print("[PASS] decomposed plans expose dependency-aware inspection and verification hints")


def test_change_planning_is_metadata_only():
    workspace, projects = make_project()
    before = (projects / "shop-app" / "app.js").read_text(encoding="utf-8")
    context = build_task_context("Fix app.js in project shop-app", str(workspace), str(projects))
    build_change_plan(context)
    after = (projects / "shop-app" / "app.js").read_text(encoding="utf-8")
    assert before == after
    print("[PASS] change planning does not execute or modify project resources")


if __name__ == "__main__":
    print("=" * 60)
    print("AZIZ AI SETUP 4.35 TEST")
    print("=" * 60)
    for name in (
        "test_dependency_and_dependent_scope",
        "test_change_scope_does_not_expand_to_all_related_files",
        "test_missing_target_is_non_assumptive",
        "test_change_plan_serializes_and_restores",
        "test_context_persists_change_plan",
        "test_decomposer_exposes_dependency_aware_hints",
        "test_change_planning_is_metadata_only",
    ):
        globals()[name]()
    print("\nSetup 4.35 tests complete.")
