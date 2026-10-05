"""Setup 4.19 gateway failure-classification tests."""
from unittest.mock import Mock, patch

from core.models.lm_studio import LMStudioGateway


def response(status, payload=None):
    r = Mock()
    r.status_code = status
    if status >= 400:
        r.raise_for_status.side_effect = __import__("requests").HTTPError(
            f"HTTP {status}", response=r
        )
    if payload is not None:
        r.json.return_value = payload
    return r


def main():
    print("=" * 60)
    print("AZIZ AI SETUP 4.19 TEST")
    print("=" * 60)

    g = LMStudioGateway(max_retries=3, retry_delay=0)
    with patch("core.models.lm_studio.requests.post", side_effect=[response(400)]):
        try:
            g.chat([{"role": "user", "content": "test"}])
        except Exception:
            pass
    assert g.stats["last_error_category"] == "permanent_http"
    assert g.stats["last_status_code"] == 400
    assert g.stats["non_retryable_failures"] == 1
    assert g.stats["last_attempts"] == 1
    print("[PASS] permanent HTTP failure is not retried")

    g = LMStudioGateway(max_retries=2, retry_delay=0)
    ok = {"choices": [{"message": {"content": "ok"}}]}
    with patch("core.models.lm_studio.requests.post", side_effect=[response(503), response(200, ok)]):
        assert g.chat([{"role": "user", "content": "test"}]) == "ok"
    assert g.stats["retryable_failures"] == 1
    assert g.stats["retry_count"] == 1
    assert g.stats["successful_requests"] == 1
    print("[PASS] transient HTTP failure remains retryable")

    g = LMStudioGateway(max_retries=0)
    with patch("core.models.lm_studio.requests.post", side_effect=[response(401)]):
        try:
            g.chat([{"role": "user", "content": "test"}])
        except Exception:
            pass
    d = g.diagnostics()
    assert d["stats"]["last_error_category"] == "permanent_http"
    assert d["stats"]["last_status_code"] == 401
    print("[PASS] diagnostics expose safe failure classification")

    print("\nSetup 4.19 tests complete.")


if __name__ == "__main__":
    main()
