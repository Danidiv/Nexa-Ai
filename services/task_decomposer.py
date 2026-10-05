"""Setup 4.31: deterministic task decomposition for coding work.

The decomposer turns a natural-language coding request into a small sequence of
meaningful subtasks. It deliberately does not call the model or execute tools;
tool selection, validation, verification, and repair remain under the existing
agent loop.
"""
from __future__ import annotations

import re
from typing import Any

from services.task_planner import PlanStep, TaskPlan
from services.task_context import TaskContext


class TaskDecomposer:
    """Build a conservative, dependency-aware plan from a coding request."""

    _QUESTION_PREFIXES = ("how", "what", "why", "explain", "tell me")

    def decompose(self, task: str, context: TaskContext | None = None) -> TaskPlan:
        task = str(task or "").strip()
        lower = task.lower()
        if not task:
            return TaskPlan(task, [])

        if lower.startswith(self._QUESTION_PREFIXES):
            return TaskPlan(task, [
                PlanStep("S1", "Understand request", "Understand the user's question and relevant context.", []),
                PlanStep("S2", "Answer", "Provide an accurate answer without modifying project resources.", ["S1"]),
                PlanStep("S3", "Verify answer", "Check that the response directly addresses the original question.", ["S2"]),
            ], context=context)

        project = self._extract_project(task)
        paths = self._extract_paths(task)
        features = self._extract_features(task)
        wants_run = self._wants_run(lower)
        wants_create = self._has_any(lower, "create", "build", "make", "generate", "develop")
        wants_modify = self._has_any(lower, "fix", "change", "edit", "update", "modify", "add", "remove", "replace", "improve")

        steps: list[PlanStep] = []
        steps.append(PlanStep(
            "S1", "Inspect context",
            self._inspect_objective(project, paths, features), []
        ))

        previous = "S1"
        if wants_create:
            objective = self._creation_objective(features, paths)
            steps.append(PlanStep("S2", "Implement structure", objective, [previous]))
            previous = "S2"
            if features:
                steps.append(PlanStep(
                    "S3", "Implement features",
                    "Implement the requested features while preserving existing project conventions and interfaces.",
                    [previous],
                ))
                previous = "S3"
        elif wants_modify:
            steps.append(PlanStep(
                "S2", "Implement changes",
                self._modification_objective(paths, features), [previous]
            ))
            previous = "S2"
        else:
            steps.append(PlanStep(
                "S2", "Satisfy request",
                "Perform the smallest safe action needed to satisfy the original request using observed context.",
                [previous],
            ))
            previous = "S2"

        if wants_run:
            steps.append(PlanStep(
                f"S{len(steps)+1}", "Run verification",
                "Run the requested or appropriate build, test, compile, or execution check and inspect its actual result.",
                [previous],
            ))
            previous = steps[-1].id
            steps.append(PlanStep(
                f"S{len(steps)+1}", "Repair if needed",
                "If verification reports a failure, diagnose the observed failure and apply the smallest repair; otherwise leave correct work unchanged.",
                [previous],
            ))
            previous = steps[-1].id
        else:
            steps.append(PlanStep(
                f"S{len(steps)+1}", "Verify result",
                "Re-read or otherwise inspect the result and compare it with every explicit requirement in the original task.",
                [previous],
            ))
            previous = steps[-1].id

        steps.append(PlanStep(
            f"S{len(steps)+1}", "Complete",
            "Report completion only when the requested result has been verified; otherwise continue the repair/verification cycle.",
            [previous],
        ))
        if context:
            self._apply_context(steps, context, project, paths)
        return TaskPlan(task, steps, context=context)

    @staticmethod
    def _apply_context(steps: list[PlanStep], context: TaskContext, project: str | None, paths: list[str]) -> None:
        """Add factual metadata hints without executing or modifying anything."""
        if not steps:
            return
        hints = []
        if project:
            if project in context.project_names:
                hints.append(f"Project '{project}' exists in the local projects directory; inspect it before editing.")
            else:
                hints.append(f"Project '{project}' was not found in the local project index; verify the exact project name before acting.")
        existing_refs = [path for path in paths if context.referenced_paths.get(path)]
        missing_refs = [path for path in paths if not context.referenced_paths.get(path)]
        if existing_refs:
            hints.append("Referenced paths currently visible: " + ", ".join(existing_refs) + ".")
        if missing_refs:
            hints.append("Referenced paths not currently visible: " + ", ".join(missing_refs) + ". Do not assume they exist; observe before deciding.")
        if context.project_names:
            hints.append("Known local projects: " + ", ".join(context.project_names[:12]) + ".")
        impact = getattr(context, "impact", None)
        if isinstance(impact, dict):
            affected = impact.get("affected_paths") or {}
            for raw_path, related in list(affected.items())[:8]:
                if related:
                    hints.append(f"Files related to {raw_path}: " + ", ".join(related[:8]) + ".")
            relationships = impact.get("relationships") or {}
            if relationships:
                hints.append("Local file relationships were statically analyzed; use them as impact hints and still read files before editing.")
        change_plan = getattr(context, "change_plan", None)
        if isinstance(change_plan, dict):
            targets = [x for x in change_plan.get("targets", []) if isinstance(x, str)]
            inspect_paths = [x for x in change_plan.get("inspect_paths", []) if isinstance(x, str)]
            verify_paths = [x for x in change_plan.get("verify_paths", []) if isinstance(x, str)]
            if targets:
                hints.append("Primary change targets: " + ", ".join(targets[:8]) + ".")
            if inspect_paths:
                hints.append("Dependency-aware inspection scope: " + ", ".join(inspect_paths[:10]) + ".")
            if verify_paths:
                hints.append("Dependency-aware verification scope: " + ", ".join(verify_paths[:10]) + ".")
        if hints:
            steps[0].objective += " Context hints: " + " ".join(hints)

    @staticmethod
    def _has_any(text: str, *words: str) -> bool:
        return any(re.search(r"\b" + re.escape(word) + r"\b", text) for word in words)

    @classmethod
    def _wants_run(cls, text: str) -> bool:
        return cls._has_any(text, "run", "execute", "test", "build", "compile", "start", "launch")

    @staticmethod
    def _extract_paths(task: str) -> list[str]:
        # Keep extraction conservative: path-like tokens only, never arbitrary prose.
        matches = re.findall(r"(?<!\w)(?:[A-Za-z]:[\\/])?[^\s,;:'\"]+\.(?:html?|css|js|jsx|ts|tsx|py|json|md|txt|yml|yaml|sql|java|cpp|c|h|vue|svelte)(?!\w)", task, re.IGNORECASE)
        return list(dict.fromkeys(matches))[:8]

    @staticmethod
    def _extract_project(task: str) -> str | None:
        match = re.search(r"\bproject\s+(?:named\s+|called\s+)?([A-Za-z0-9_.-]+)", task, re.IGNORECASE)
        return match.group(1) if match else None

    @staticmethod
    def _extract_features(task: str) -> list[str]:
        lower = task.lower()
        known = {
            "login": "authentication/login",
            "sign up": "registration/sign-up",
            "signup": "registration/sign-up",
            "dashboard": "dashboard",
            "admin": "admin functionality",
            "cart": "shopping cart",
            "checkout": "checkout",
            "payment": "payment flow",
            "search": "search",
            "database": "database/data persistence",
            "api": "API integration",
            "responsive": "responsive UI",
            "dark mode": "dark mode",
            "form": "forms",
        }
        return list(dict.fromkeys(label for marker, label in known.items() if marker in lower))

    @staticmethod
    def _inspect_objective(project: str | None, paths: list[str], features: list[str]) -> str:
        if project:
            return f"Inspect project '{project}' and its relevant files before changing anything."
        if paths:
            return "Inspect the referenced files (" + ", ".join(paths) + ") and their surrounding project context before changing anything."
        if features:
            return "Inspect the existing project structure and relevant implementation areas before adding the requested features."
        return "Observe the relevant workspace or project context before acting on the original request."

    @staticmethod
    def _creation_objective(features: list[str], paths: list[str]) -> str:
        if features:
            return "Create or extend only the required project structure for: " + ", ".join(features) + "."
        if paths:
            return "Create the requested resources using the referenced files (" + ", ".join(paths) + ") and existing project conventions."
        return "Create the minimum project structure and resources required by the original request."

    @staticmethod
    def _modification_objective(paths: list[str], features: list[str]) -> str:
        if paths and features:
            return "Read the existing implementation, then make the smallest changes needed in the referenced resources for: " + ", ".join(features) + "."
        if paths:
            return "Read the referenced resources (" + ", ".join(paths) + ") and make the smallest changes required by the original request."
        if features:
            return "Locate the relevant implementation and make the smallest changes required for: " + ", ".join(features) + "."
        return "Read the relevant existing resources and make the smallest safe change required by the original request."


def decompose_task(task: str) -> TaskPlan:
    """Convenience API used by the agent session."""
    return TaskDecomposer().decompose(task)
