from services.completion_build_diagnostics import build_build_diagnostics, valid_build_diagnostics


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.62 TEST")
    print("============================================================")
    obj = build_build_diagnostics("sample", ["a", "b"], ["evidence"])
    assert valid_build_diagnostics(obj); print("[PASS] compile/build error normalization built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_build_diagnostics(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_build_diagnostics(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.62 tests complete.")

if __name__ == "__main__":
    main()
