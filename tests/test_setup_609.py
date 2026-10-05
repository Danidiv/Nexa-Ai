from services.completion_repair_plan import build_repair_plan, valid_repair_plan, RepairPlan

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.09 TEST")
    print("============================================================")
    obj = build_repair_plan("sample", ["a", "b"], ["evidence"])
    assert valid_repair_plan(obj); print("[PASS] repair plan built")
    assert obj.repairs == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_repair_plan(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["repairs"] = ["tampered"]
    assert not valid_repair_plan(RepairPlan(obj.name, tuple(bad["repairs"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.09 tests complete.")

if __name__ == "__main__":
    main()
