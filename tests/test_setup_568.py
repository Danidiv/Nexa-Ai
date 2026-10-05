from services.completion_smoke_test_planning import build_smoke_test_planning, valid_smoke_test_planning


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.68 TEST")
    print("============================================================")
    obj = build_smoke_test_planning("sample", ["a", "b"], ["evidence"])
    assert valid_smoke_test_planning(obj); print("[PASS] post-deploy smoke checks built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_smoke_test_planning(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_smoke_test_planning(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.68 tests complete.")

if __name__ == "__main__":
    main()
