from services.completion_test_generation_plan import build_test_generation_plan, valid_test_generation_plan, TestGenerationPlan

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.05 TEST")
    print("============================================================")
    obj = build_test_generation_plan("sample", ["a", "b"], ["evidence"])
    assert valid_test_generation_plan(obj); print("[PASS] test generation plan built")
    assert obj.cases == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_test_generation_plan(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["cases"] = ["tampered"]
    assert not valid_test_generation_plan(TestGenerationPlan(obj.name, tuple(bad["cases"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.05 tests complete.")

if __name__ == "__main__":
    main()
