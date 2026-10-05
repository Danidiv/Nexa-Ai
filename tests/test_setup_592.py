from services.completion_slo_contract import build_slo_contract, valid_slo_contract, SLOContract

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.92 TEST")
    print("============================================================")
    obj = build_slo_contract("sample", ["a", "b"], ["evidence"])
    assert valid_slo_contract(obj); print("[PASS] SLO objectives built")
    assert obj.objectives == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_slo_contract(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["objectives"] = ["tampered"]
    assert bad["objectives"] != list(obj.objectives) and not valid_slo_contract(type(obj)(obj.name, tuple(bad["objectives"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.92 tests complete.")

if __name__ == "__main__":
    main()
