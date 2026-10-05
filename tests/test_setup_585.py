from services.completion_traffic_readiness_gate import build_traffic_readiness_gate, valid_traffic_readiness_gate


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.85 TEST")
    print("============================================================")
    obj = build_traffic_readiness_gate("sample", ["a", "b"], ["evidence"])
    assert valid_traffic_readiness_gate(obj); print("[PASS] traffic readiness gate built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_traffic_readiness_gate(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_traffic_readiness_gate(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.85 tests complete.")

if __name__ == "__main__":
    main()
