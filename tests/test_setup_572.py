from services.completion_build_execution_policy import build_contract, valid_contract

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.72 TEST")
    print("============================================================")
    obj = build_contract("sample", ["python -m py_compile app.py"], ["PATH"])
    assert valid_contract(obj); print("[PASS] build execution policy built")
    assert obj.name == "sample"; print("[PASS] contract data preserved")
    assert obj.digest and valid_contract(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["name"] = "tampered"
    bad_obj = type(obj)(bad["name"], obj.commands, obj.environment_keys, obj.digest)
    assert not valid_contract(bad_obj); print("[PASS] tamper rejected")
    print("Setup 5.72 tests complete.")

if __name__ == "__main__":
    main()
