from services.completion_preview_readiness import build_preview_readiness, valid_preview_readiness


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.64 TEST")
    print("============================================================")
    obj = build_preview_readiness("sample", ["a", "b"], ["evidence"])
    assert valid_preview_readiness(obj); print("[PASS] preview startup readiness contract built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_preview_readiness(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_preview_readiness(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.64 tests complete.")

if __name__ == "__main__":
    main()
