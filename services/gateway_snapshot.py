"""Setup 4.27: validated, JSON-safe gateway runtime snapshot persistence."""
from __future__ import annotations
import json
from copy import deepcopy

class GatewaySnapshot:
    VERSION = 1
    MAX_HISTORY = 1000
    REQUIRED = {"snapshot_version", "health", "telemetry", "request_history", "stats", "circuit"}

    @classmethod
    def validate(cls, state):
        if not isinstance(state, dict):
            raise TypeError("gateway snapshot must be a dictionary")
        if state.get("snapshot_version") != cls.VERSION:
            raise ValueError(f"unsupported gateway snapshot version: {state.get('snapshot_version')}")
        missing = cls.REQUIRED - set(state)
        if missing:
            raise ValueError(f"gateway snapshot missing fields: {sorted(missing)}")
        if not isinstance(state["health"], dict) or not isinstance(state["telemetry"], dict):
            raise ValueError("health and telemetry must be dictionaries")
        history = state["request_history"]
        if not isinstance(history, list) or len(history) > cls.MAX_HISTORY:
            raise ValueError("request_history must be a bounded list")
        safe_history = []
        allowed = {"request_id", "outcome", "attempts", "duration_seconds", "error_category", "status_code", "timestamp"}
        for item in history:
            if not isinstance(item, dict):
                raise ValueError("request history entries must be dictionaries")
            safe_history.append({k: item[k] for k in allowed if k in item})
        if not isinstance(state["stats"], dict) or not isinstance(state["circuit"], dict):
            raise ValueError("stats and circuit must be dictionaries")
        result = deepcopy(state)
        result["request_history"] = safe_history
        # Force a JSON round-trip to reject non-JSON-safe values before mutation.
        try:
            json.dumps(result, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("gateway snapshot is not JSON-safe") from exc
        return result

    @classmethod
    def serialize(cls, state):
        return cls.validate(state)
