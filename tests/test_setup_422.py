"""AZIZ AI SETUP 4.22 TEST"""

from services.gateway_health import GatewayHealth


def main() -> None:
    print("=" * 60)
    print("AZIZ AI SETUP 4.22 TEST")
    print("=" * 60)

    health = GatewayHealth()
    health.record_success()
    health.record_failure()
    health.record_failure()
    stats = health.snapshot()

    assert stats["total_requests"] == 3
    assert stats["successful_requests"] == 1
    assert stats["failed_requests"] == 2
    print("[PASS] gateway health statistics are accurate")

    assert stats["consecutive_failures"] == 2
    assert stats["has_recent_failure"] is True
    print("[PASS] consecutive failure state is tracked safely")

    health.record_success()
    assert health.snapshot()["consecutive_failures"] == 0
    print("[PASS] successful request clears consecutive failures")

    health.reset()
    assert health.snapshot() == {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "consecutive_failures": 0,
        "has_recent_failure": False,
    }
    print("[PASS] gateway health can be reset")

    print("\nSetup 4.22 tests complete.")


if __name__ == "__main__":
    main()
