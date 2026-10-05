from services.completion_root_cause_analysis import build_root_cause_analysis, valid_root_cause_analysis, RootCauseAnalysis

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.08 TEST")
    print("============================================================")
    obj = build_root_cause_analysis("sample", ["a", "b"], ["evidence"])
    assert valid_root_cause_analysis(obj); print("[PASS] root cause analysis built")
    assert obj.causes == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_root_cause_analysis(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["causes"] = ["tampered"]
    assert not valid_root_cause_analysis(RootCauseAnalysis(obj.name, tuple(bad["causes"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.08 tests complete.")

if __name__ == "__main__":
    main()
