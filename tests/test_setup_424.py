"""AZIZ AI SETUP 4.24 TEST - unified gateway health and telemetry."""
from unittest.mock import Mock, patch
import requests

from core.models.lm_studio import LMStudioGateway


def response(status=200, content="ok"):
    r = Mock()
    r.status_code = status
    if status >= 400:
        r.raise_for_status.side_effect = requests.HTTPError(f"HTTP {status}", response=r)
    else:
        r.raise_for_status.return_value = None
    r.json.return_value = {"choices": [{"message": {"content": content}}]}
    return r


def main():
    print("=" * 60)
    print("AZIZ AI SETUP 4.24 TEST")
    print("=" * 60)

    g = LMStudioGateway(max_retries=1, retry_delay=0, retry_jitter=0)
    with patch("core.models.lm_studio.requests.post", side_effect=[response(503), response(200, "integrated")]):
        assert g.chat([{"role": "user", "content": "test"}]) == "integrated"
    assert g.health["total_requests"] == 1
    assert g.health["successful_requests"] == 1
    assert g.health["failed_requests"] == 0
    assert g.telemetry["count"] == 1
    assert g.telemetry["min_seconds"] >= 0
    print("[PASS] gateway health and telemetry are integrated")

    g = LMStudioGateway(max_retries=0, retry_delay=0)
    with patch("core.models.lm_studio.requests.post", side_effect=[response(503)]):
        try:
            g.chat([{"role": "user", "content": "fail"}])
        except requests.HTTPError:
            pass
    assert g.health["total_requests"] == 1
    assert g.health["failed_requests"] == 1
    assert g.health["consecutive_failures"] == 1
    assert g.telemetry["count"] == 1
    print("[PASS] failed requests update health and timing safely")

    d = g.diagnostics()
    assert "health" in d and "telemetry" in d and "stats" in d
    assert d["health"]["failed_requests"] == 1
    assert set(d["telemetry"]) == {"count", "total_seconds", "average_seconds", "min_seconds", "max_seconds"}
    print("[PASS] unified diagnostics expose safe health and telemetry")

    g.reset_stats()
    assert g.health["total_requests"] == 0
    assert g.telemetry["count"] == 0
    print("[PASS] gateway reset clears integrated runtime metrics")

    print("\nSetup 4.24 tests complete.")


if __name__ == "__main__":
    main()
