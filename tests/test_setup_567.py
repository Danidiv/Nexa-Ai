from services.completion_deployment_planning import build_deployment_planning, valid_deployment_planning


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.67 TEST")
    print("============================================================")
    obj = build_deployment_planning("sample", ["a", "b"], ["evidence"])
    assert valid_deployment_planning(obj); print("[PASS] bounded deployment plan built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_deployment_planning(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_deployment_planning(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.67 tests complete.")

if __name__ == "__main__":
    main()
