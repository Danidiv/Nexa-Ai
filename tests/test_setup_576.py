from services.completion_deployment_observability import build_contract, valid_contract

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.76 TEST")
    print("============================================================")
    obj = build_contract("sample", ["latency"], ["deploy_started"])
    assert valid_contract(obj); print("[PASS] deployment observability built")
    assert obj.name == "sample"; print("[PASS] contract data preserved")
    assert obj.digest and valid_contract(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["name"] = "tampered"
    bad_obj = type(obj)(bad["name"], obj.metrics, obj.events, obj.digest)
    assert not valid_contract(bad_obj); print("[PASS] tamper rejected")
    print("Setup 5.76 tests complete.")

if __name__ == "__main__":
    main()
