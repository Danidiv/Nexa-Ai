"""Setup 4.34 - bounded file relationship and impact analysis."""
from pathlib import Path
from tempfile import TemporaryDirectory

from services.task_context import build_task_context
from services.task_impact import TaskImpact, build_task_impact
from services.task_decomposer import TaskDecomposer
from services.task_planner import TaskPlan


def main():
    print("=" * 60)
    print("AZIZ AI SETUP 4.34 TEST")
    print("=" * 60)

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        workspace = root / "workspace"
        projects = root / "projects"
        project = projects / "shop-app"
        project.mkdir(parents=True)
        (project / "app.js").write_text("import { cart } from './cart.js';\nimport './styles.css';\n", encoding="utf-8")
        (project / "cart.js").write_text("export const cart = [];\n", encoding="utf-8")
        (project / "styles.css").write_text("body { margin: 0; }\n", encoding="utf-8")
        (project / "index.html").write_text('<script src="./app.js"></script>\n', encoding="utf-8")

        context = build_task_context("Fix app.js in project shop-app", str(workspace), str(projects))
        assert isinstance(context.impact, dict)
        relationships = context.impact["relationships"]
        reverse = context.impact["reverse_relationships"]
        assert "cart.js" in relationships["app.js"]
        assert "styles.css" in relationships["app.js"]
        assert "app.js" in reverse["cart.js"]
        print("[PASS] static analysis discovers bounded local file relationships")

        assert "cart.js" in context.impact["affected_paths"]["app.js"]
        assert "styles.css" in context.impact["affected_paths"]["app.js"]
        print("[PASS] referenced files expose directly related impact hints")

        plan = TaskDecomposer().decompose("Fix app.js in project shop-app", context=context)
        objective = plan.steps[0].objective
        assert "cart.js" in objective and "styles.css" in objective
        print("[PASS] decomposed plans include file-impact context hints")

        encoded = plan.to_dict()
        restored = TaskPlan.from_dict(encoded)
        assert restored is not None
        assert restored.context is not None
        assert restored.context.impact["affected_paths"]["app.js"]
        print("[PASS] impact context persists through plan serialization")

        raw = build_task_impact("Fix app.js in project shop-app", str(workspace), str(projects), {"app.js": True})
        encoded_impact = raw.to_dict()
        restored_impact = TaskImpact.from_dict(encoded_impact)
        assert restored_impact is not None
        assert "cart.js" in restored_impact.affected_paths["app.js"]
        print("[PASS] impact graph is JSON-safe and restores correctly")

        # Bounded analysis must not execute source code or leave generated files.
        assert not list(project.glob("*.pyc"))
        assert len(restored_impact.analyzed_files) <= 60
        assert all(len(v) <= 12 for v in restored_impact.relationships.values())
        print("[PASS] impact analysis remains bounded and non-executing")

    print("\nSetup 4.34 tests complete.")


if __name__ == "__main__":
    main()
