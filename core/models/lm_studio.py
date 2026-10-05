import os
import time
import random
import uuid
import json
import os
import tempfile
from datetime import datetime, timezone
from copy import deepcopy

import requests

from .gateway import ModelGateway
from services.gateway_health import GatewayHealth
from services.request_telemetry import RequestTelemetry
from services.request_history import RequestHistory
from services.gateway_snapshot import GatewaySnapshot
from services.gateway_events import GatewayEventStream
from services.gateway_recovery import GatewayRuntimeRecovery


class LMStudioGateway(ModelGateway):
    """LM Studio OpenAI-compatible gateway with bounded retry support."""

    def __init__(
        self,
        base_url=None,
        model=None,
        timeout=None,
        max_retries=None,
        retry_delay=None,
        retry_backoff_max=None,
        retry_jitter=None,
        request_history_limit=None,
        snapshot_path=None,
        event_log_limit=None,
        event_log_path=None,
        auto_restore=None,
    ):
        self.base_url = (base_url or os.getenv("AZIZ_LM_STUDIO_URL", "http://localhost:1234/v1")).rstrip("/")
        self.model = model or os.getenv("AZIZ_MODEL", "qwen/qwen3.5-9b")
        self.timeout = timeout if timeout is not None else (
            float(os.getenv("AZIZ_CONNECT_TIMEOUT", "10")),
            float(os.getenv("AZIZ_READ_TIMEOUT", "300")),
        )
        self.max_retries = max(0, int(os.getenv("AZIZ_MODEL_RETRIES", "2"))) if max_retries is None else max(0, int(max_retries))
        self.retry_delay = max(0.0, float(os.getenv("AZIZ_RETRY_DELAY", "1.0"))) if retry_delay is None else max(0.0, float(retry_delay))
        # Setup 4.20: capped exponential backoff with optional jitter.
        self.retry_backoff_max = max(0.0, float(os.getenv("AZIZ_RETRY_BACKOFF_MAX", "30"))) if retry_backoff_max is None else max(0.0, float(retry_backoff_max))
        self.retry_jitter = max(0.0, float(os.getenv("AZIZ_RETRY_JITTER", "0.25"))) if retry_jitter is None else max(0.0, float(retry_jitter))

        # Setup 4.18: circuit protection for repeated model failures.
        self.circuit_failure_threshold = max(1, int(os.getenv("AZIZ_CIRCUIT_FAILURE_THRESHOLD", "3")))
        self.circuit_cooldown = max(0.0, float(os.getenv("AZIZ_CIRCUIT_COOLDOWN", "30")))
        self._consecutive_failures = 0
        # Setup 4.24: integrate persistent-safe health and request timing telemetry.
        self._health = GatewayHealth()
        self._telemetry = RequestTelemetry()
        self.request_history_limit = max(1, int(os.getenv("AZIZ_REQUEST_HISTORY_LIMIT", "50"))) if request_history_limit is None else max(1, int(request_history_limit))
        self._request_history = RequestHistory(self.request_history_limit)
        self._circuit_opened_at = None
        self.snapshot_path = snapshot_path or os.getenv("AZIZ_GATEWAY_SNAPSHOT_PATH", "gateway_runtime_snapshot.json")
        self.event_log_limit = max(1, int(os.getenv("AZIZ_GATEWAY_EVENT_LOG_LIMIT", "200"))) if event_log_limit is None else max(1, int(event_log_limit))
        self._events = GatewayEventStream(self.event_log_limit)
        self.event_log_path = event_log_path or os.getenv("AZIZ_GATEWAY_EVENT_LOG_PATH", "gateway_runtime_events.jsonl")
        self.auto_restore = (os.getenv("AZIZ_GATEWAY_AUTO_RESTORE", "0").strip().lower() in {"1", "true", "yes", "on"}) if auto_restore is None else bool(auto_restore)
        self._recovery = GatewayRuntimeRecovery(self)

        # Setup 4.17: lightweight gateway observability.
        self._stats = {
            "retryable_failures": 0,
            "non_retryable_failures": 0,
            "last_error_category": None,
            "last_status_code": None,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "retry_count": 0,
            "last_attempts": 0,
            "last_latency_seconds": None,
            "last_error": None,
            "circuit_blocked_requests": 0,
            "consecutive_failures": 0,
            "circuit_open": False,
        }
        self._last_recovery = None
        if self.auto_restore:
            self._last_recovery = self.restore_runtime()

    @property
    def endpoint(self):
        return f"{self.base_url}/chat/completions"

    @property
    def health(self):
        """Return a safe snapshot of logical gateway health."""
        return self._health.snapshot()

    @property
    def telemetry(self):
        """Return a safe snapshot of logical chat request timing."""
        return self._telemetry.snapshot()

    @property
    def request_history(self):
        """Return a safe snapshot of recent logical requests."""
        return self._request_history.snapshot()

    @property
    def events(self):
        """Return a safe snapshot of recent gateway runtime events."""
        return self._events.snapshot()

    @property
    def stats(self):
        """Return a safe snapshot of gateway request statistics."""
        return deepcopy(self._stats)

    def reset_stats(self):
        """Reset request statistics without changing gateway configuration."""
        for key in self._stats:
            self._stats[key] = None if key in {"last_latency_seconds", "last_error"} else 0
        self._stats["circuit_open"] = self._circuit_is_open()
        self._stats["consecutive_failures"] = self._consecutive_failures
        self._health.reset()
        self._telemetry.reset()
        self._request_history.reset()
        self._events.reset()

    def reset_circuit_breaker(self):
        """Close the circuit and clear consecutive model failures."""
        self._consecutive_failures = 0
        self._circuit_opened_at = None
        self._stats["consecutive_failures"] = 0
        self._stats["circuit_open"] = False

    def _circuit_is_open(self):
        if self._circuit_opened_at is None:
            return False
        elapsed = time.monotonic() - self._circuit_opened_at
        if elapsed >= self.circuit_cooldown:
            self.reset_circuit_breaker()
            return False
        return True

    def diagnostics(self):
        """Return configuration and runtime diagnostics without secrets."""
        return {
            "endpoint": self.endpoint,
            "model": self.model,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "retry_backoff_max": self.retry_backoff_max,
            "retry_jitter": self.retry_jitter,
            "circuit_failure_threshold": self.circuit_failure_threshold,
            "circuit_cooldown": self.circuit_cooldown,
            "circuit_open": self._circuit_is_open(),
            "consecutive_failures": self._consecutive_failures,
            "stats": self.stats,
            "health": self.health,
            "telemetry": self.telemetry,
            "request_history_limit": self.request_history_limit,
            "request_history": self.request_history,
            "snapshot_version": GatewaySnapshot.VERSION,
            "snapshot_path": self.snapshot_path,
            "event_log_limit": self.event_log_limit,
            "event_log_path": self.event_log_path,
            "events": self.events,
            "auto_restore": self.auto_restore,
            "last_recovery": deepcopy(self._last_recovery),
        }

    def export_state(self):
        """Return a JSON-safe runtime snapshot without prompts or payloads."""
        circuit_open = self._circuit_is_open()
        remaining = 0.0
        if circuit_open and self._circuit_opened_at is not None:
            remaining = max(0.0, self.circuit_cooldown - (time.monotonic() - self._circuit_opened_at))
        return {
            "snapshot_version": GatewaySnapshot.VERSION,
            "health": self.health,
            "telemetry": self.telemetry,
            "request_history": self.request_history,
            "stats": self.stats,
            "circuit": {
                "consecutive_failures": self._consecutive_failures,
                "open": circuit_open,
                "remaining_cooldown_seconds": round(remaining, 6),
            },
        }

    def restore_state(self, state):
        """Restore a validated runtime snapshot. Configuration is never replaced."""
        normalized = GatewaySnapshot.validate(state)
        self._health = GatewayHealth.from_state(normalized["health"])
        # Telemetry has no from_state in older setups; restore through its internal safe stats.
        self._telemetry.reset()
        t = normalized["telemetry"]
        if t.get("count", 0):
            # Reconstruct aggregate timing exactly enough for public snapshots.
            self._telemetry._stats.count = int(t["count"])
            self._telemetry._stats.total_seconds = float(t["total_seconds"])
            self._telemetry._stats.min_seconds = float(t["min_seconds"])
            self._telemetry._stats.max_seconds = float(t["max_seconds"])
        self._request_history.reset()
        for entry in normalized["request_history"]:
            self._request_history.record(entry)
        self._stats = deepcopy(normalized["stats"])
        circuit = normalized["circuit"]
        self._consecutive_failures = int(circuit["consecutive_failures"])
        remaining = max(0.0, float(circuit.get("remaining_cooldown_seconds", 0.0)))
        self._circuit_opened_at = time.monotonic() if circuit.get("open") and remaining > 0 else None
        self._stats["consecutive_failures"] = self._consecutive_failures
        self._stats["circuit_open"] = self._circuit_is_open()
        return True

    def save_snapshot(self, path=None):
        """Atomically save the current runtime snapshot to a JSON file."""
        target = os.path.abspath(path or self.snapshot_path)
        parent = os.path.dirname(target) or os.getcwd()
        os.makedirs(parent, exist_ok=True)
        payload = GatewaySnapshot.serialize(self.export_state())
        fd, temp_path = tempfile.mkstemp(prefix=".aziz-gateway-", suffix=".tmp", dir=parent, text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, target)
        except Exception:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise
        self._events.record("snapshot_saved")
        return target

    def load_snapshot(self, path=None):
        """Load and restore a runtime snapshot from a JSON file."""
        target = os.path.abspath(path or self.snapshot_path)
        with open(target, "r", encoding="utf-8") as f:
            state = json.load(f)
        self.restore_state(state)
        self._events.record("snapshot_loaded")
        return True

    def save_event_log(self, path=None):
        """Persist the bounded audit stream as secret-safe JSONL."""
        return self._events.save_jsonl(path or self.event_log_path)

    def load_event_log(self, path=None):
        """Load a bounded audit stream from secret-safe JSONL."""
        return self._events.load_jsonl(path or self.event_log_path)

    def restore_runtime(self, snapshot_path=None, event_log_path=None):
        """Restore persisted runtime state and return a safe recovery report."""
        report = self._recovery.restore(snapshot_path, event_log_path)
        self._last_recovery = deepcopy(report)
        self._events.record(
            "runtime_recovery",
            outcome="restored" if report["restored_any"] else "nothing_to_restore",
        )
        return deepcopy(report)

    def health_check(self):
        """Return True when LM Studio's models endpoint is reachable."""
        response = requests.get(
            f"{self.base_url}/models",
            timeout=self.timeout,
        )
        response.raise_for_status()
        return True

    @staticmethod
    def _classify_error(exc):
        """Classify failures so retry logic does not blindly retry permanent errors."""
        status = getattr(getattr(exc, "response", None), "status_code", None)
        if status is not None:
            if status in {408, 425, 429} or 500 <= status <= 599:
                return "transient_http", status, True
            return "permanent_http", status, False
        if isinstance(exc, requests.Timeout):
            return "timeout", None, True
        if isinstance(exc, requests.ConnectionError):
            return "connection", None, True
        if isinstance(exc, requests.RequestException):
            return "request", None, True
        if isinstance(exc, ValueError):
            return "invalid_response", None, True
        return "unknown", None, False

    def _record_request_history(self, request_id, outcome, attempts, started, error_category=None, status_code=None):
        self._request_history.record({
            "request_id": request_id,
            "outcome": outcome,
            "attempts": attempts,
            "duration_seconds": round(time.monotonic() - started, 6),
            "error_category": error_category,
            "status_code": status_code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def chat(self, messages, temperature: float = 0.0, max_tokens=None) -> str:
        request_id = str(uuid.uuid4())
        request_started = time.monotonic()
        self._events.record("request_started", request_id)
        if self._circuit_is_open():
            self._stats["circuit_blocked_requests"] += 1
            self._record_request_history(request_id, "circuit_blocked", 0, request_started, "circuit_open", None)
            self._events.record("request_blocked", request_id, outcome="circuit_blocked", error_category="circuit_open")
            self._stats["circuit_open"] = True
            raise RuntimeError(
                f"LM Studio circuit breaker is open; retry after {self.circuit_cooldown:g} seconds"
            )

        request_measurement = self._telemetry.measure()
        request_measurement.__enter__()
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        self._stats["total_requests"] += 1
        started = time.monotonic()
        last_error = None
        attempts = 0
        for attempt in range(self.max_retries + 1):
            attempts = attempt + 1
            try:
                response = requests.post(
                    self.endpoint,
                    json=payload,
                    timeout=self.timeout,
                )
                if response.status_code == 400:
                    # LM Studio commonly returns 400 for model-id/schema/context
                    # validation. Preserve the server body and, for a model-id
                    # failure, autonomously discover a loaded model instead of
                    # forcing the user to edit configuration just to continue.
                    try:
                        detail = response.json()
                    except ValueError:
                        detail = response.text.strip()
                    detail_text = json.dumps(detail, ensure_ascii=False).lower()
                    if any(token in detail_text for token in ("model", "not found", "does not exist")):
                        try:
                            models_resp = requests.get(f"{self.base_url}/models", timeout=(5, 10))
                            models_resp.raise_for_status()
                            models = (models_resp.json().get("data") or [])
                            ids = [str(item.get("id")) for item in models if isinstance(item, dict) and item.get("id")]
                            if ids and self.model not in ids:
                                old_model = self.model
                                # Prefer the model family the user explicitly configured.
                                # LM Studio may expose a full id such as
                                # `mistralai/ministral-3-3b` while AZIZ uses `mistralai-3-3b`.
                                configured = str(old_model).lower()
                                preferred = []
                                if "mistral" in configured:
                                    preferred = [m for m in ids if "mistral" in m.lower() and "embed" not in m.lower()]
                                elif "qwen" in configured:
                                    preferred = [m for m in ids if "qwen" in m.lower() and "embed" not in m.lower()]
                                candidates = preferred or [m for m in ids if "embed" not in m.lower()] or ids
                                self.model = candidates[0]
                                payload["model"] = self.model
                                self._events.record("model_fallback", request_id, old_model=old_model, new_model=self.model)
                                continue
                        except Exception:
                            pass
                    raise requests.HTTPError(
                        f"LM Studio 400 Bad Request: {detail}",
                        response=response,
                    )
                response.raise_for_status()
                data = response.json()
                choices = data.get("choices") or []
                if not choices or not isinstance(choices[0], dict):
                    raise ValueError("LM Studio returned no valid choices")
                message = choices[0].get("message") or {}
                content = message.get("content")
                if content is None:
                    raise ValueError("LM Studio response has no message content")

                self._stats["successful_requests"] += 1
                self._consecutive_failures = 0
                self._circuit_opened_at = None
                self._stats["consecutive_failures"] = 0
                self._stats["circuit_open"] = False
                self._stats["last_attempts"] = attempts
                self._stats["last_latency_seconds"] = round(time.monotonic() - started, 6)
                self._stats["last_error"] = None
                self._health.record_success()
                request_measurement.finish()
                self._record_request_history(request_id, "success", attempts, request_started)
                self._events.record("request_completed", request_id, attempt=attempts, outcome="success")
                return str(content)
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                category, status_code, retryable = self._classify_error(exc)
                self._stats["last_error"] = f"{type(exc).__name__}: {exc}"
                self._stats["last_error_category"] = category
                self._stats["last_status_code"] = status_code
                if retryable:
                    self._stats["retryable_failures"] += 1
                else:
                    self._stats["non_retryable_failures"] += 1

                # Setup 4.19: permanent HTTP failures should fail immediately.
                if not retryable:
                    self._stats["failed_requests"] += 1
                    self._consecutive_failures += 1
                    self._stats["consecutive_failures"] = self._consecutive_failures
                    if self._consecutive_failures >= self.circuit_failure_threshold:
                        self._circuit_opened_at = time.monotonic()
                    self._stats["circuit_open"] = self._circuit_is_open()
                    self._stats["last_attempts"] = attempts
                    self._stats["last_latency_seconds"] = round(time.monotonic() - started, 6)
                    self._health.record_failure()
                    request_measurement.finish()
                    self._record_request_history(request_id, "failure", attempts, request_started, category, status_code)
                    self._events.record("request_failed", request_id, attempt=attempts, outcome="failure", error_category=category, status_code=status_code)
                    raise

                self._stats["retry_count"] += 1 if attempt < self.max_retries else 0
                if attempt >= self.max_retries:
                    self._stats["failed_requests"] += 1
                    self._consecutive_failures += 1
                    self._stats["consecutive_failures"] = self._consecutive_failures
                    if self._consecutive_failures >= self.circuit_failure_threshold:
                        self._circuit_opened_at = time.monotonic()
                    self._stats["circuit_open"] = self._circuit_is_open()
                    self._stats["last_attempts"] = attempts
                    self._stats["last_latency_seconds"] = round(time.monotonic() - started, 6)
                    self._health.record_failure()
                    request_measurement.finish()
                    self._record_request_history(request_id, "failure", attempts, request_started, category, status_code)
                    self._events.record("request_failed", request_id, attempt=attempts, outcome="failure", error_category=category, status_code=status_code)
                    raise
                delay = min(
                    self.retry_backoff_max,
                    self.retry_delay * (2 ** attempt),
                )
                if self.retry_jitter > 0 and delay > 0:
                    delay += random.uniform(0.0, delay * self.retry_jitter)
                time.sleep(delay)

        raise last_error
