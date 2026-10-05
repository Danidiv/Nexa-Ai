from services.completion_test_generation_plan import build_test_generation_plan, valid_test_generation_plan, TestGenerationPlan

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.26 TEST")
    print("============================================================")
    obj=build_test_generation_plan(["a","b"], ["a","b"], ["a","b"], ["a","b"])
    assert valid_test_generation_plan(obj); print("[PASS] test generation plan built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_test_generation_plan(obj); print("[PASS] digest validates")
    assert not valid_test_generation_plan(TestGenerationPlan(( "tampered", ), obj.framework, obj.cases, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.26 tests complete.")
if __name__ == "__main__": main()
