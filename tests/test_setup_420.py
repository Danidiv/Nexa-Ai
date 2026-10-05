"""Setup 4.20 retry backoff tests."""
from unittest.mock import Mock, patch
import requests

from core.models.lm_studio import LMStudioGateway


def response(status, payload=None):
    r = Mock()
    r.status_code = status
    if status >= 400:
        r.raise_for_status.side_effect = requests.HTTPError(f"HTTP {status}", response=r)
    if payload is not None:
        r.json.return_value = payload
    return r


def main():
    print("=" * 60)
    print("AZIZ AI SETUP 4.20 TEST")
    print("=" * 60)

    g = LMStudioGateway(max_retries=3, retry_delay=1, retry_jitter=0)
    ok = {"choices": [{"message": {"content": "ok"}}]}
    with patch("core.models.lm_studio.requests.post", side_effect=[response(503), response(503), response(503), response(200, ok)]), patch("core.models.lm_studio.time.sleep") as sleep:
        assert g.chat([{"role": "user", "content": "test"}]) == "ok"
    assert [c.args[0] for c in sleep.call_args_list] == [1, 2, 4]
    print("[PASS] retry delay uses exponential backoff")

    g = LMStudioGateway(max_retries=4, retry_delay=10, retry_backoff_max=12, retry_jitter=0)
    with patch("core.models.lm_studio.requests.post", side_effect=[response(503)] * 4 + [response(200, ok)]), patch("core.models.lm_studio.time.sleep") as sleep:
        assert g.chat([{"role": "user", "content": "test"}]) == "ok"
    assert [c.args[0] for c in sleep.call_args_list] == [10, 12, 12, 12]
    print("[PASS] retry backoff is capped")

    g = LMStudioGateway(max_retries=1, retry_delay=1, retry_jitter=0.25)
    d = g.diagnostics()
    assert d["retry_backoff_max"] == 30
    assert d["retry_jitter"] == 0.25
    print("[PASS] backoff settings are exposed safely")

    print("\nSetup 4.20 tests complete.")


if __name__ == "__main__":
    main()
