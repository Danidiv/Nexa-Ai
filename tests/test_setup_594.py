from services.completion_feature_flag_safety import build_feature_flag_safety, valid_feature_flag_safety, FeatureFlagSafety

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.94 TEST")
    print("============================================================")
    obj = build_feature_flag_safety("sample", ["a", "b"], ["evidence"])
    assert valid_feature_flag_safety(obj); print("[PASS] feature flags built")
    assert obj.flags == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_feature_flag_safety(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["flags"] = ["tampered"]
    assert bad["flags"] != list(obj.flags) and not valid_feature_flag_safety(type(obj)(obj.name, tuple(bad["flags"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.94 tests complete.")

if __name__ == "__main__":
    main()
