from services.completion_deployment_environment import build_deployment_environment, valid_deployment_environment


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.65 TEST")
    print("============================================================")
    obj = build_deployment_environment("sample", ["a", "b"], ["evidence"])
    assert valid_deployment_environment(obj); print("[PASS] runtime environment mapping built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_deployment_environment(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_deployment_environment(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.65 tests complete.")

if __name__ == "__main__":
    main()
