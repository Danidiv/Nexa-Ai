from services.completion_deployment_health import build_contract, valid_contract

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.75 TEST")
    print("============================================================")
    obj = build_contract("sample", ["http://localhost:3000/health"], ["status"], True)
    assert valid_contract(obj); print("[PASS] deployment health verification built")
    assert obj.name == "sample"; print("[PASS] contract data preserved")
    assert obj.digest and valid_contract(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["name"] = "tampered"
    bad_obj = type(obj)(bad["name"], obj.endpoints, obj.checks, obj.healthy, obj.digest)
    assert not valid_contract(bad_obj); print("[PASS] tamper rejected")
    print("Setup 5.75 tests complete.")

if __name__ == "__main__":
    main()
