"""AZIZ AI SETUP 4.18 TEST - circuit protection."""
import core.models.lm_studio as lm_module
from core.models.lm_studio import LMStudioGateway


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"choices": [{"message": {"content": "Circuit recovered."}}]}


def main():
    print("=" * 60)
    print("AZIZ AI SETUP 4.18 TEST")
    print("=" * 60)

    original_post = lm_module.requests.post
    original_sleep = lm_module.time.sleep

    calls = {"count": 0}

    def failing_post(*args, **kwargs):
        calls["count"] += 1
        raise lm_module.requests.RequestException("simulated LM Studio outage")

    try:
        lm_module.requests.post = failing_post
        lm_module.time.sleep = lambda _: None
        gateway = LMStudioGateway(max_retries=0, retry_delay=0)
        gateway.circuit_failure_threshold = 2
        gateway.circuit_cooldown = 60

        for _ in range(2):
            try:
                gateway.chat([{"role": "user", "content": "test"}])
            except lm_module.requests.RequestException:
                pass

        assert gateway.diagnostics()["circuit_open"] is True
        assert gateway.diagnostics()["consecutive_failures"] == 2
        assert calls["count"] == 2
        print("[PASS] repeated model failures open the circuit")

        try:
            gateway.chat([{"role": "user", "content": "blocked"}])
            raise AssertionError("circuit should have blocked the request")
        except RuntimeError as exc:
            assert "circuit breaker is open" in str(exc).lower()
        assert calls["count"] == 2
        assert gateway.stats["circuit_blocked_requests"] == 1
        print("[PASS] open circuit blocks additional model requests")

        gateway._circuit_opened_at = lm_module.time.monotonic() - gateway.circuit_cooldown - 1
        gateway.circuit_cooldown = 0
        lm_module.requests.post = lambda *args, **kwargs: FakeResponse()
        result = gateway.chat([{"role": "user", "content": "recover"}])
        assert result == "Circuit recovered."
        assert gateway.diagnostics()["circuit_open"] is False
        assert gateway.diagnostics()["consecutive_failures"] == 0
        print("[PASS] cooldown recovery closes the circuit")

        gateway.reset_circuit_breaker()
        assert gateway.diagnostics()["circuit_open"] is False
        assert gateway.diagnostics()["consecutive_failures"] == 0
        print("[PASS] circuit breaker can be reset safely")
    finally:
        lm_module.requests.post = original_post
        lm_module.time.sleep = original_sleep

    print("\nSetup 4.18 tests complete.")


if __name__ == "__main__":
    main()
