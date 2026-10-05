from services.completion_environment_parity import build_contract, valid_contract

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.73 TEST")
    print("============================================================")
    obj = build_contract("sample", ["PYTHON=3.12"], ["PYTHON=3.12"], [])
    assert valid_contract(obj); print("[PASS] environment parity contract built")
    assert obj.name == "sample"; print("[PASS] contract data preserved")
    assert obj.digest and valid_contract(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["name"] = "tampered"
    bad_obj = type(obj)(bad["name"], obj.expected, obj.actual, obj.mismatches, obj.digest)
    assert not valid_contract(bad_obj); print("[PASS] tamper rejected")
    print("Setup 5.73 tests complete.")

if __name__ == "__main__":
    main()
