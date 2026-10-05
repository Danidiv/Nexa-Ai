"""Setup 4.30: lightweight, deterministic task planning for the agent.

The planner does not call the model. It converts the original user task into a
small, resumable plan that the model can use as execution guidance. This keeps
planning deterministic, testable, and safe while leaving actual tool selection
to the model and existing validation layer.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any
import re

from services.task_context import TaskContext


@dataclass
class PlanStep:
    id: str
    title: str
    objective: str
    depends_on: list[str]
    status: str = "pending"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TaskPlan:
    VERSION = 1

    def __init__(self, task: str, steps: list[PlanStep] | None = None, context: TaskContext | None = None):
        self.task = str(task or "").strip()
        self.steps = list(steps or [])
        self.revision = 0
        self._current_step_id = None
        self.context = context

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_version": self.VERSION,
            "task": self.task,
            "steps": [step.to_dict() for step in self.steps],
            "revision": int(self.revision),
            "context": self.context.to_dict() if self.context else None,
        }

    @classmethod
    def from_dict(cls, data: Any) -> "TaskPlan | None":
        if not isinstance(data, dict) or data.get("plan_version") != cls.VERSION:
            return None
        task = data.get("task")
        raw_steps = data.get("steps")
        if not isinstance(task, str) or not isinstance(raw_steps, list):
            return None
        steps: list[PlanStep] = []
        for raw in raw_steps:
            if not isinstance(raw, dict):
                return None
            required = ("id", "title", "objective", "depends_on", "status")
            if any(key not in raw for key in required):
                return None
            if not all(isinstance(raw[key], str) for key in ("id", "title", "objective", "status")):
                return None
            if not isinstance(raw["depends_on"], list) or not all(isinstance(x, str) for x in raw["depends_on"]):
                return None
            if raw["status"] not in {"pending", "in_progress", "completed", "blocked"}:
                return None
            steps.append(PlanStep(raw["id"], raw["title"], raw["objective"], list(raw["depends_on"]), raw["status"]))
        plan = cls(task, steps, TaskContext.from_dict(data.get("context")))
        try:
            plan.revision = max(0, int(data.get("revision", 0) or 0))
        except (TypeError, ValueError):
            plan.revision = 0
        return plan

    def next_step(self) -> PlanStep | None:
        completed = {s.id for s in self.steps if s.status == "completed"}
        for step in self.steps:
            if step.status == "pending" and all(dep in completed for dep in step.depends_on):
                return step
        return None

    def mark_completed(self, step_id: str) -> bool:
        for step in self.steps:
            if step.id == step_id:
                step.status = "completed"
                return True
        return False

    def adapt_after_result(self, action: str, result: Any) -> PlanStep | None:
        """Adapt the advisory plan after an observed tool result.

        Failures cause a bounded repair checkpoint to be inserted before the
        failed step. The original step remains pending, so the agent can retry
        it after the repair. This never executes a tool or overrides the main
        agent lifecycle.
        """
        current = next((s for s in self.steps if s.id == getattr(self, "_current_step_id", None)), None)
        if current is None:
            return None
        text = str(result or "")
        lower = text.lower()
        if not any(marker in lower for marker in (
            "error:", "failed:", "failure:", "traceback", "not found",
            "permission denied", "access denied", "exception:", "unknown tool",
        )):
            return None

        # Do not create duplicate repair checkpoints for the same failed step.
        existing = [
            s for s in self.steps
            if s.id.startswith("R") and s.id in current.depends_on
        ]
        if existing:
            current.status = "pending"
            self._current_step_id = existing[-1].id
            return existing[-1]

        repair_id = f"R{self.revision + 1}"
        if any(s.id == repair_id for s in self.steps):
            repair_id = f"R{self.revision + 1}_{len(self.steps)}"
        if any(marker in lower for marker in ("file not found", "folder not found", "project not found", "not found")):
            title = "Locate missing resource"
            objective = "Use the observed failure to locate the correct file, folder, or project before retrying the failed task."
        elif any(marker in lower for marker in ("test", "build", "compile", "traceback", "exception", "syntax error")):
            title = "Diagnose verification failure"
            objective = "Inspect the observed verification failure, identify its concrete cause, and prepare the smallest safe repair before retrying."
        else:
            title = "Diagnose failure"
            objective = "Inspect the observed tool failure, determine its concrete cause, and prepare the smallest safe repair before retrying."

        repair = PlanStep(repair_id, title, objective, list(current.depends_on))
        index = self.steps.index(current)
        self.steps.insert(index, repair)
        current.depends_on = [repair.id]
        current.status = "pending"
        self.revision += 1
        self._current_step_id = repair.id
        return repair

    def bind_current_step(self, step_id: str | None) -> None:
        self._current_step_id = step_id

    def summary(self) -> str:
        if not self.steps:
            return "No plan steps."
        parts = []
        for step in self.steps:
            parts.append(f"{step.id}:{step.title}[{step.status}]")
        return " → ".join(parts)


class TaskPlanner:
    """Create a conservative execution plan from a user's original task."""

    _QUESTION_WORDS = ("how", "what", "why", "explain", "tell me")

    def create_plan(self, task: str) -> TaskPlan:
        task = str(task or "").strip()
        lower = task.lower()
        steps: list[PlanStep] = []

        if not task:
            return TaskPlan(task, steps)

        # Questions/explanations need no filesystem action; the plan makes this
        # explicit so the agent does not invent edits for informational tasks.
        if lower.startswith(self._QUESTION_WORDS):
            steps.append(PlanStep("S1", "Understand", "Answer the user's question using the available context.", []))
            steps.append(PlanStep("S2", "Verify", "Check that the answer addresses the original question before responding.", ["S1"]))
            return TaskPlan(task, steps)

        is_project = bool(re.search(r"\bproject\b", lower)) or bool(re.search(r"\bprojects?[/\\]", lower))
        is_read = any(word in lower for word in ("read ", "show ", "list ", "display ", "check "))
        is_create = any(word in lower for word in ("create", "make", "build", "generate"))
        is_modify = any(word in lower for word in ("fix", "change", "edit", "update", "modify", "add", "remove", "replace"))
        is_run = any(word in lower for word in ("run", "execute", "test", "build", "compile"))

        if is_project:
            steps.append(PlanStep("S1", "Inspect project", "Identify and inspect the requested project before acting.", []))
        else:
            steps.append(PlanStep("S1", "Inspect context", "Observe the relevant workspace files or context before acting.", []))

        if is_create:
            objective = "Create only the files and structure required by the original request."
        elif is_modify:
            objective = "Read existing resources and make the smallest change required by the original request."
        elif is_read:
            objective = "Inspect and report the requested resources without modifying them."
        else:
            objective = "Determine the smallest safe action needed to satisfy the original request."
        steps.append(PlanStep("S2", "Execute", objective, ["S1"]))

        if is_run:
            steps.append(PlanStep("S3", "Run verification", "Run the requested or appropriate verification and inspect its actual result.", ["S2"]))
            steps.append(PlanStep("S4", "Complete", "If verification succeeds, report completion; otherwise repair and verify again.", ["S3"]))
        else:
            steps.append(PlanStep("S3", "Verify", "Re-read or otherwise verify the changed/result resource against the original requirements.", ["S2"]))
            steps.append(PlanStep("S4", "Complete", "Return a final answer only after the result is verified.", ["S3"]))

        return TaskPlan(task, steps)
