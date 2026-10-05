from services.completion_release_deployment_agent import build_contract, valid_contract

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.80 TEST")
    print("============================================================")
    obj = build_contract("sample", ["preflight","deploy","smoke"], ["evidence"], True)
    assert valid_contract(obj); print("[PASS] integrated release/deployment workflow built")
    assert obj.name == "sample"; print("[PASS] contract data preserved")
    assert obj.digest and valid_contract(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["name"] = "tampered"
    bad_obj = type(obj)(bad["name"], obj.stages, obj.evidence, obj.ready, obj.digest)
    assert not valid_contract(bad_obj); print("[PASS] tamper rejected")
    print("Setup 5.80 tests complete.")

if __name__ == "__main__":
    main()
