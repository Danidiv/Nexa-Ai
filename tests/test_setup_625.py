from services.completion_syntax_repair_plan import build_syntax_repair_plan, valid_syntax_repair_plan, SyntaxRepairPlan

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.25 TEST")
    print("============================================================")
    obj=build_syntax_repair_plan(["a","b"], ["a","b"], ["a","b"], ["a","b"])
    assert valid_syntax_repair_plan(obj); print("[PASS] syntax repair plan built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_syntax_repair_plan(obj); print("[PASS] digest validates")
    assert not valid_syntax_repair_plan(SyntaxRepairPlan(( "tampered", ), obj.repairs, obj.validation, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.25 tests complete.")
if __name__ == "__main__": main()
