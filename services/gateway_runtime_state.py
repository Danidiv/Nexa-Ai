"""Setup 4.26: JSON-safe gateway runtime snapshot validation."""
from __future__ import annotations
from typing import Any

SNAPSHOT_VERSION = 1


def _non_negative_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def validate_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize a gateway runtime snapshot without secrets."""
    if not isinstance(snapshot, dict):
        raise TypeError("gateway runtime state must be a dictionary")
    version = snapshot.get("version", SNAPSHOT_VERSION)
    if version != SNAPSHOT_VERSION:
        raise ValueError(f"unsupported gateway runtime state version: {version!r}")

    health = snapshot.get("health", {})
    telemetry = snapshot.get("telemetry", {})
    request_history = snapshot.get("request_history", [])
    stats = snapshot.get("stats", {})
    circuit = snapshot.get("circuit", {})

    if not isinstance(health, dict) or not isinstance(telemetry, dict) or not isinstance(stats, dict) or not isinstance(circuit, dict):
        raise TypeError("gateway runtime state sections must be dictionaries")
    if not isinstance(request_history, list):
        raise TypeError("request_history must be a list")

    normalized = {
        "version": SNAPSHOT_VERSION,
        "health": dict(health),
        "telemetry": dict(telemetry),
        "request_history": [dict(item) for item in request_history if isinstance(item, dict)],
        "stats": dict(stats),
        "circuit": dict(circuit),
    }

    _non_negative_int(normalized["health"].get("total_requests", 0), "health.total_requests")
    _non_negative_int(normalized["health"].get("successful_requests", 0), "health.successful_requests")
    _non_negative_int(normalized["health"].get("failed_requests", 0), "health.failed_requests")
    _non_negative_int(normalized["health"].get("consecutive_failures", 0), "health.consecutive_failures")

    for name in ("count",):
        _non_negative_int(normalized["telemetry"].get(name, 0), f"telemetry.{name}")

    remaining = normalized["circuit"].get("remaining_cooldown_seconds", 0.0)
    if isinstance(remaining, bool) or not isinstance(remaining, (int, float)) or remaining < 0:
        raise ValueError("circuit.remaining_cooldown_seconds must be non-negative")
    normalized["circuit"]["remaining_cooldown_seconds"] = float(remaining)
    normalized["circuit"]["open"] = bool(normalized["circuit"].get("open", False))
    return normalized
