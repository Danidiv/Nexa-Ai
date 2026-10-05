from services.completion_dependency_install_planning import build_dependency_install_planning, valid_dependency_install_planning


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.63 TEST")
    print("============================================================")
    obj = build_dependency_install_planning("sample", ["a", "b"], ["evidence"])
    assert valid_dependency_install_planning(obj); print("[PASS] safe dependency change plan built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_dependency_install_planning(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_dependency_install_planning(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.63 tests complete.")

if __name__ == "__main__":
    main()
