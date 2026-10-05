"""Setup 4.23: JSON-safe gateway health persistence."""
from __future__ import annotations
from dataclasses import dataclass
from time import monotonic
from typing import Any

@dataclass
class GatewayHealth:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    consecutive_failures: int = 0
    last_failure_at: float | None = None

    def record_success(self) -> None:
        self.total_requests += 1
        self.successful_requests += 1
        self.consecutive_failures = 0

    def record_failure(self) -> None:
        self.total_requests += 1
        self.failed_requests += 1
        self.consecutive_failures += 1
        self.last_failure_at = monotonic()

    def reset(self) -> None:
        self.total_requests = self.successful_requests = self.failed_requests = 0
        self.consecutive_failures = 0
        self.last_failure_at = None

    def snapshot(self) -> dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "consecutive_failures": self.consecutive_failures,
            "has_recent_failure": self.last_failure_at is not None,
        }

    def export_state(self) -> dict[str, Any]:
        return self.snapshot()

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "GatewayHealth":
        if not isinstance(state, dict):
            raise TypeError("gateway health state must be a dictionary")
        values = {}
        for name in ("total_requests", "successful_requests", "failed_requests", "consecutive_failures"):
            value = state.get(name, 0)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
            values[name] = value
        obj = cls(**values)
        if state.get("has_recent_failure", False):
            obj.last_failure_at = monotonic()
        return obj
