from services.completion_resource_efficiency import build_resource_efficiency, valid_resource_efficiency, ResourceEfficiency

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.99 TEST")
    print("============================================================")
    obj = build_resource_efficiency("sample", ["a", "b"], ["evidence"])
    assert valid_resource_efficiency(obj); print("[PASS] resource budgets built")
    assert obj.budgets == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_resource_efficiency(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["budgets"] = ["tampered"]
    assert bad["budgets"] != list(obj.budgets) and not valid_resource_efficiency(type(obj)(obj.name, tuple(bad["budgets"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.99 tests complete.")

if __name__ == "__main__":
    main()
