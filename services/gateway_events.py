"""Setup 4.28: bounded, secret-safe gateway runtime event stream."""
from __future__ import annotations
from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Any
import json
import os
import tempfile


class GatewayEventStream:
    """Thread-safe bounded audit events containing metadata, never request payloads."""

    ALLOWED = {"event_id", "event", "request_id", "attempt", "outcome", "error_category", "status_code", "timestamp"}

    def __init__(self, max_entries: int = 200):
        self.max_entries = max(1, int(max_entries))
        self._entries = deque(maxlen=self.max_entries)
        self._lock = Lock()

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    def record(self, event: str, request_id: str | None = None, **fields: Any) -> dict[str, Any]:
        safe = {"event_id": __import__("uuid").uuid4().hex, "event": str(event), "timestamp": self._timestamp()}
        if request_id is not None:
            safe["request_id"] = str(request_id)
        for key in self.ALLOWED - {"event_id", "event", "request_id", "timestamp"}:
            if key in fields and fields[key] is not None:
                safe[key] = fields[key]
        try:
            json.dumps(safe, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("gateway event is not JSON-safe") from exc
        with self._lock:
            self._entries.append(dict(safe))
        return dict(safe)

    def snapshot(self) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(item) for item in self._entries]

    def reset(self) -> None:
        with self._lock:
            self._entries.clear()

    def save_jsonl(self, path: str) -> str:
        """Atomically replace a JSONL event file using only safe event metadata."""
        target = os.path.abspath(path)
        parent = os.path.dirname(target) or os.getcwd()
        os.makedirs(parent, exist_ok=True)
        fd, temp_path = tempfile.mkstemp(prefix=".aziz-events-", suffix=".tmp", dir=parent, text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                for event in self.snapshot():
                    f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, target)
        except Exception:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise
        return target

    def load_jsonl(self, path: str) -> int:
        """Load at most the configured number of safe events from a JSONL file."""
        target = os.path.abspath(path)
        entries = []
        with open(target, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                item = json.loads(line)
                if not isinstance(item, dict):
                    raise ValueError("gateway event must be a dictionary")
                safe = {k: item[k] for k in self.ALLOWED if k in item}
                if safe.get("event") is None or safe.get("event_id") is None or safe.get("timestamp") is None:
                    raise ValueError("gateway event missing required fields")
                json.dumps(safe, ensure_ascii=False)
                entries.append(safe)
        entries = entries[-self.max_entries:]
        with self._lock:
            self._entries.clear()
            self._entries.extend(entries)
        return len(entries)
