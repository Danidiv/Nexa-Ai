"""AZIZ AI SETUP 4.16 TEST - resilient LM Studio gateway."""
import os

from core.models.lm_studio import LMStudioGateway
import core.models.lm_studio as lm_module


class FakeResponse:
    def __init__(self, content="Gateway retry works."):
        self.content = content

    def raise_for_status(self):
        return None

    def json(self):
        return {"choices": [{"message": {"content": self.content}}]}


def main():
    print("=" * 60)
    print("AZIZ AI SETUP 4.16 TEST")
    print("=" * 60)

    original_post = lm_module.requests.post
    original_sleep = lm_module.time.sleep
    calls = {"count": 0}

    def fake_post(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            import requests
            raise requests.ConnectionError("temporary LM Studio failure")
        return FakeResponse()

    try:
        lm_module.requests.post = fake_post
        lm_module.time.sleep = lambda _: None
        gateway = LMStudioGateway(max_retries=1, retry_delay=0)
        result = gateway.chat([{"role": "user", "content": "test"}])
        assert result == "Gateway retry works."
        assert calls["count"] == 2
        print("[PASS] transient model failure is retried")
        assert gateway.endpoint.endswith("/chat/completions")
        print("[PASS] LM Studio endpoint is constructed correctly")
        assert gateway.max_retries == 1
        assert gateway.timeout[0] > 0 and gateway.timeout[1] > 0
        print("[PASS] bounded timeout and retry settings are active")
    finally:
        lm_module.requests.post = original_post
        lm_module.time.sleep = original_sleep

    print("\nSetup 4.16 tests complete.")


if __name__ == "__main__":
    main()
