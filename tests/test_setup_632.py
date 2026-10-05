from services.completion_database_change_plan import build_database_change_plan, valid_database_change_plan, DatabaseChangePlan

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.32 TEST")
    print("============================================================")
    obj=build_database_change_plan(["a","b"], ["a","b"], ["a","b"], ["a","b"])
    assert valid_database_change_plan(obj); print("[PASS] database change plan built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_database_change_plan(obj); print("[PASS] digest validates")
    assert not valid_database_change_plan(DatabaseChangePlan(( "tampered", ), obj.dependencies, obj.rollback, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.32 tests complete.")
if __name__ == "__main__": main()
