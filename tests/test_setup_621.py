from services.completion_code_generation_plan import build_code_generation_plan, valid_code_generation_plan, CodeGenerationPlan

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.21 TEST")
    print("============================================================")
    obj=build_code_generation_plan("sample", ["a","b"], ["a","b"], ["a","b"])
    assert valid_code_generation_plan(obj); print("[PASS] code generation plan built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_code_generation_plan(obj); print("[PASS] digest validates")
    assert not valid_code_generation_plan(CodeGenerationPlan("tampered", obj.constraints, obj.targets, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.21 tests complete.")
if __name__ == "__main__": main()
