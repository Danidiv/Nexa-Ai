from services.completion_remediation_planning import build_remediation_planning, valid_remediation_planning


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.88 TEST")
    print("============================================================")
    obj = build_remediation_planning("sample", ["a", "b"], ["evidence"])
    assert valid_remediation_planning(obj); print("[PASS] automated remediation plan built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_remediation_planning(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_remediation_planning(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.88 tests complete.")

if __name__ == "__main__":
    main()
