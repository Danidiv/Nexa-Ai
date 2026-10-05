"""AZIZ AI SETUP 4.23 TEST"""
import json
from services.gateway_health import GatewayHealth

def main():
    print("=" * 60)
    print("AZIZ AI SETUP 4.23 TEST")
    print("=" * 60)
    h = GatewayHealth()
    h.record_success()
    h.record_failure()
    h.record_failure()
    state = h.export_state()
    json.dumps(state)
    print("[PASS] gateway health state is JSON serializable")
    r = GatewayHealth.from_state(state)
    assert (r.total_requests, r.successful_requests, r.failed_requests, r.consecutive_failures) == (3, 1, 2, 2)
    print("[PASS] gateway health state restores correctly")
    r.record_success()
    assert r.consecutive_failures == 0 and r.total_requests == 4
    print("[PASS] restored health state remains operational")
    try:
        GatewayHealth.from_state({"total_requests": -1})
        raise AssertionError("invalid state accepted")
    except ValueError:
        pass
    print("[PASS] invalid health state is rejected safely")
    print("\nSetup 4.23 tests complete.")

if __name__ == "__main__":
    main()
