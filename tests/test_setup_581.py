from services.completion_deployment_snapshot import build_deployment_snapshot, valid_deployment_snapshot


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.81 TEST")
    print("============================================================")
    obj = build_deployment_snapshot("sample", ["a", "b"], ["evidence"])
    assert valid_deployment_snapshot(obj); print("[PASS] deployment snapshot built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_deployment_snapshot(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_deployment_snapshot(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.81 tests complete.")

if __name__ == "__main__":
    main()
