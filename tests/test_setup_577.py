from services.completion_rollback_execution import build_contract, valid_contract

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.77 TEST")
    print("============================================================")
    obj = build_contract("sample", ["restore"], ["backup_verified"])
    assert valid_contract(obj); print("[PASS] rollback execution plan built")
    assert obj.name == "sample"; print("[PASS] contract data preserved")
    assert obj.digest and valid_contract(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["name"] = "tampered"
    bad_obj = type(obj)(bad["name"], obj.steps, obj.safety_gates, obj.digest)
    assert not valid_contract(bad_obj); print("[PASS] tamper rejected")
    print("Setup 5.77 tests complete.")

if __name__ == "__main__":
    main()
