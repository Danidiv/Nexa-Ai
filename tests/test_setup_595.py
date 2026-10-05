from services.completion_configuration_drift import build_configuration_drift, valid_configuration_drift, ConfigurationDrift

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.95 TEST")
    print("============================================================")
    obj = build_configuration_drift("sample", ["a", "b"], ["evidence"])
    assert valid_configuration_drift(obj); print("[PASS] drift changes built")
    assert obj.changes == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_configuration_drift(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["changes"] = ["tampered"]
    assert bad["changes"] != list(obj.changes) and not valid_configuration_drift(type(obj)(obj.name, tuple(bad["changes"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.95 tests complete.")

if __name__ == "__main__":
    main()
