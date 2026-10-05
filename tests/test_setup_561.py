from services.completion_build_artifact_intelligence import build_build_artifact_intelligence, valid_build_artifact_intelligence


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.61 TEST")
    print("============================================================")
    obj = build_build_artifact_intelligence("sample", ["a", "b"], ["evidence"])
    assert valid_build_artifact_intelligence(obj); print("[PASS] artifact graph and build outputs built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_build_artifact_intelligence(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_build_artifact_intelligence(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.61 tests complete.")

if __name__ == "__main__":
    main()
