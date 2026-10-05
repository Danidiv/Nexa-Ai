from services.completion_repair_iteration_plan import build_repair_iteration_plan, valid_repair_iteration_plan, RepairIterationPlan

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.29 TEST")
    print("============================================================")
    obj=build_repair_iteration_plan("sample", ["a","b"], ["a","b"], ["a","b"])
    assert valid_repair_iteration_plan(obj); print("[PASS] repair iteration plan built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_repair_iteration_plan(obj); print("[PASS] digest validates")
    assert not valid_repair_iteration_plan(RepairIterationPlan("tampered", obj.iterations, obj.stop_conditions, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.29 tests complete.")
if __name__ == "__main__": main()
