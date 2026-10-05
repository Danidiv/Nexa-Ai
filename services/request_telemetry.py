"""Setup 4.21/4.24 safe request timing telemetry."""
from dataclasses import dataclass
from threading import Lock
from time import monotonic


@dataclass
class RequestTimingStats:
    count: int = 0
    total_seconds: float = 0.0
    min_seconds: float | None = None
    max_seconds: float | None = None

    def record(self, seconds: float):
        value = max(0.0, float(seconds))
        self.count += 1
        self.total_seconds += value
        self.min_seconds = value if self.min_seconds is None else min(self.min_seconds, value)
        self.max_seconds = value if self.max_seconds is None else max(self.max_seconds, value)

    def snapshot(self):
        return {
            "count": self.count,
            "total_seconds": round(self.total_seconds, 6),
            "average_seconds": round(self.total_seconds / self.count, 6) if self.count else 0.0,
            "min_seconds": round(self.min_seconds, 6) if self.min_seconds is not None else 0.0,
            "max_seconds": round(self.max_seconds, 6) if self.max_seconds is not None else 0.0,
        }


class RequestTelemetry:
    def __init__(self):
        self._lock = Lock()
        self._stats = RequestTimingStats()

    def record(self, seconds):
        with self._lock:
            self._stats.record(seconds)

    def snapshot(self):
        with self._lock:
            return dict(self._stats.snapshot())

    def reset(self):
        with self._lock:
            self._stats = RequestTimingStats()

    def measure(self):
        return RequestMeasurement(self)


class RequestMeasurement:
    def __init__(self, telemetry):
        self.telemetry = telemetry
        self.started = monotonic()
        self._finished = False

    def finish(self):
        if self._finished:
            return 0.0
        self._finished = True
        elapsed = monotonic() - self.started
        self.telemetry.record(elapsed)
        return elapsed

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.finish()
