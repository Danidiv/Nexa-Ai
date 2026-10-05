from services.completion_deployment_secret_safety import build_deployment_secret_safety, valid_deployment_secret_safety


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.66 TEST")
    print("============================================================")
    obj = build_deployment_secret_safety("sample", ["a", "b"], ["evidence"])
    assert valid_deployment_secret_safety(obj); print("[PASS] secret-safe environment handling built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_deployment_secret_safety(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_deployment_secret_safety(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.66 tests complete.")

if __name__ == "__main__":
    main()
