from services.completion_test_discovery import build_test_discovery, valid_test_discovery, TestDiscovery

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.04 TEST")
    print("============================================================")
    obj = build_test_discovery("sample", ["a", "b"], ["evidence"])
    assert valid_test_discovery(obj); print("[PASS] test discovery built")
    assert obj.tests == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_test_discovery(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["tests"] = ["tampered"]
    assert not valid_test_discovery(TestDiscovery(obj.name, tuple(bad["tests"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.04 tests complete.")

if __name__ == "__main__":
    main()
