from services.completion_service_health import build_service_health, valid_service_health


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.82 TEST")
    print("============================================================")
    obj = build_service_health("sample", ["a", "b"], ["evidence"])
    assert valid_service_health(obj); print("[PASS] service health contract built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_service_health(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_service_health(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.82 tests complete.")

if __name__ == "__main__":
    main()
