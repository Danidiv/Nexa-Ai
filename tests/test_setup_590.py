from services.completion_production_operations_agent import build_production_operations_agent, valid_production_operations_agent


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.90 TEST")
    print("============================================================")
    obj = build_production_operations_agent("sample", ["a", "b"], ["evidence"])
    assert valid_production_operations_agent(obj); print("[PASS] integrated production operations workflow built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_production_operations_agent(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_production_operations_agent(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.90 tests complete.")

if __name__ == "__main__":
    main()
