from services.completion_rollback_readiness import build_rollback_readiness, valid_rollback_readiness


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.69 TEST")
    print("============================================================")
    obj = build_rollback_readiness("sample", ["a", "b"], ["evidence"])
    assert valid_rollback_readiness(obj); print("[PASS] rollback safety contract built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_rollback_readiness(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_rollback_readiness(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.69 tests complete.")

if __name__ == "__main__":
    main()
