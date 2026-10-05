"""AZIZ AI SETUP 4.17 TEST - gateway observability."""
import core.models.lm_studio as lm_module
from core.models.lm_studio import LMStudioGateway


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"choices": [{"message": {"content": "Observability works."}}]}


def main():
    print("=" * 60)
    print("AZIZ AI SETUP 4.17 TEST")
    print("=" * 60)

    original_post = lm_module.requests.post
    original_sleep = lm_module.time.sleep

    def fake_post(*args, **kwargs):
        return FakeResponse()

    try:
        lm_module.requests.post = fake_post
        lm_module.time.sleep = lambda _: None
        gateway = LMStudioGateway(max_retries=2, retry_delay=0)
        result = gateway.chat([{"role": "user", "content": "test"}])
        assert result == "Observability works."
        print("[PASS] successful request is recorded")

        stats = gateway.stats
        assert stats["total_requests"] == 1
        assert stats["successful_requests"] == 1
        assert stats["failed_requests"] == 0
        assert stats["last_attempts"] == 1
        assert stats["last_latency_seconds"] is not None
        print("[PASS] request statistics are accurate")

        diagnostics = gateway.diagnostics()
        assert diagnostics["endpoint"].endswith("/chat/completions")
        assert diagnostics["stats"]["successful_requests"] == 1
        assert "stats" in diagnostics
        print("[PASS] diagnostics expose safe gateway state")

        gateway.reset_stats()
        assert gateway.stats["total_requests"] == 0
        assert gateway.stats["successful_requests"] == 0
        assert gateway.stats["last_error"] is None
        print("[PASS] statistics can be reset")
    finally:
        lm_module.requests.post = original_post
        lm_module.time.sleep = original_sleep

    print("\nSetup 4.17 tests complete.")


if __name__ == "__main__":
    main()
