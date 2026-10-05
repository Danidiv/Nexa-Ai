from services.completion_runtime_config_validation import build_runtime_config_validation, valid_runtime_config_validation


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.83 TEST")
    print("============================================================")
    obj = build_runtime_config_validation("sample", ["a", "b"], ["evidence"])
    assert valid_runtime_config_validation(obj); print("[PASS] runtime config validation built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_runtime_config_validation(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_runtime_config_validation(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.83 tests complete.")

if __name__ == "__main__":
    main()
