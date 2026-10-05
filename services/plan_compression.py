"""Small, model-driven recovery for oversized project plans.

A local model may ignore the planner's size instruction and return a large
file list.  That should be a recoverable planning condition, not a hard build
failure.  This module asks the same model to compress/replan the list while
preserving the requested features and the required entry file.
"""
from __future__ import annotations

import json

from services.real_react_builder import _strip_fences

MAX_PLAN_FILES = 10
MAX_REPLAN_ATTEMPTS = 3


def replan_oversized_plan(gateway, description: str, items: list, *, entry_path: str, extension: str) -> list:
    """Compress an oversized raw JSON plan to <=10 files.

    The returned value is still raw dictionaries so the caller can apply its
    domain-specific path/schema validation afterwards.
    """
    current = items
    for attempt in range(1, MAX_REPLAN_ATTEMPTS + 1):
        other_rule = (
            f"All other files must be valid component paths ending in {extension!r}. "
            if extension else
            "All other files must use safe relative paths appropriate for the project. "
        )
        prompt = (
            "The previous project plan is too large. Replan/compress it into "
            f"AT MOST {MAX_PLAN_FILES} files while preserving ALL requested "
            "features and interactions. Merge closely related UI sections "
            "into shared components instead of deleting features. Keep the "
            f"required entry file exactly {entry_path!r}. " + other_rule +
            "Prefer fewer, richer components over many tiny components. "
            "Return ONLY a JSON array. Each item must contain exactly "
            '"path" and "purpose".\n\n'
            f"Original request:\n{description.strip()}\n\n"
            f"Previous oversized plan ({len(current)} files):\n"
            f"{json.dumps(current, indent=2)}\n\n"
            f"Compression attempt {attempt}/{MAX_REPLAN_ATTEMPTS}."
        )
        raw = gateway.chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a project-plan compression specialist. "
                        "Preserve functionality, do not invent unnecessary files, "
                        "and output ONLY valid JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=1000,
        )
        cleaned = _strip_fences(raw)
        try:
            candidate = json.loads(cleaned)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, list) and candidate and len(candidate) <= MAX_PLAN_FILES:
            return candidate
        if isinstance(candidate, list):
            current = candidate

    raise ValueError(
        f"planner returned {len(current)} files and automatic compression could not "
        f"reduce the plan to {MAX_PLAN_FILES} files after {MAX_REPLAN_ATTEMPTS} attempts"
    )
