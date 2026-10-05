from services.completion_endpoint_contract_validation import build_endpoint_contract_validation, valid_endpoint_contract_validation


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.84 TEST")
    print("============================================================")
    obj = build_endpoint_contract_validation("sample", ["a", "b"], ["evidence"])
    assert valid_endpoint_contract_validation(obj); print("[PASS] endpoint contract validation built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_endpoint_contract_validation(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_endpoint_contract_validation(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.84 tests complete.")

if __name__ == "__main__":
    main()
