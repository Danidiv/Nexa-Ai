"""Setup 4.25: bounded, secret-safe logical gateway request history."""
from __future__ import annotations
from collections import deque
from threading import Lock
from typing import Any

class RequestHistory:
    """Thread-safe bounded history of completed logical gateway requests."""
    def __init__(self, max_entries: int = 50):
        self.max_entries = max(1, int(max_entries))
        self._lock = Lock()
        self._entries = deque(maxlen=self.max_entries)
    def record(self, entry: dict[str, Any]) -> None:
        if not isinstance(entry, dict):
            raise TypeError("request history entry must be a dictionary")
        allowed = {"request_id", "outcome", "attempts", "duration_seconds", "error_category", "status_code", "timestamp"}
        safe = {k: entry[k] for k in allowed if k in entry}
        with self._lock:
            self._entries.append(dict(safe))
    def snapshot(self) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(item) for item in self._entries]
    def reset(self) -> None:
        with self._lock:
            self._entries.clear()
    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)
