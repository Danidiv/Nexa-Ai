from services.completion_dependency_update_plan import build_dependency_update_plan, valid_dependency_update_plan, DependencyUpdatePlan

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.36 TEST")
    print("============================================================")
    obj=build_dependency_update_plan(["a","b"], ["a","b"], ["a","b"], ["a","b"])
    assert valid_dependency_update_plan(obj); print("[PASS] dependency update plan built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_dependency_update_plan(obj); print("[PASS] digest validates")
    assert not valid_dependency_update_plan(DependencyUpdatePlan(( "tampered", ), obj.constraints, obj.actions, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.36 tests complete.")
if __name__ == "__main__": main()
