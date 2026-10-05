from services.completion_release_manifest import build_contract, valid_contract

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.71 TEST")
    print("============================================================")
    obj = build_contract("sample", ["artifact-a","artifact-b"], ["version"])
    assert valid_contract(obj); print("[PASS] release manifest built")
    assert obj.name == "sample"; print("[PASS] contract data preserved")
    assert obj.digest and valid_contract(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["name"] = "tampered"
    bad_obj = type(obj)(bad["name"], obj.artifacts, obj.metadata, obj.digest)
    assert not valid_contract(bad_obj); print("[PASS] tamper rejected")
    print("Setup 5.71 tests complete.")

if __name__ == "__main__":
    main()
