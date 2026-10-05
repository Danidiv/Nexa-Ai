"""Setup 4.39: freshness binding for post-change completion evidence.

Completion evidence from an earlier change must not satisfy verification for a
later change to the same resource.  This module provides a small, deterministic
change epoch that can be persisted with agent state and attached to evidence.
"""
from __future__ import annotations

from typing import Any

VERSION = 2
MAX_EPOCH = 2_147_483_647


def normalize_epoch(value: Any) -> int:
    try:
        epoch = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(epoch, MAX_EPOCH))


def next_change_epoch(current: Any) -> int:
    epoch = normalize_epoch(current)
    return 1 if epoch >= MAX_EPOCH else epoch + 1


def is_fresh(evidence: Any, current_epoch: Any) -> bool:
    """Return True only when evidence belongs to the current change epoch."""
    if not isinstance(evidence, dict):
        return False
    return normalize_epoch(evidence.get("change_epoch", 0)) == normalize_epoch(current_epoch)


def normalize_resource_key(value: Any) -> str:
    return str(value or "").replace("\\", "/").lstrip("./")


def resource_generation(generations: Any, resource: Any) -> int:
    if not isinstance(generations, dict):
        return 0
    key = normalize_resource_key(resource)
    return normalize_epoch(generations.get(key, 0))


def is_resource_fresh(evidence: Any, resource: Any, generations: Any) -> bool:
    if not isinstance(evidence, dict):
        return False
    expected = resource_generation(generations, resource)
    if expected == 0:
        return is_fresh(evidence, evidence.get("change_epoch", 0))
    return normalize_epoch(evidence.get("change_epoch", 0)) >= expected
