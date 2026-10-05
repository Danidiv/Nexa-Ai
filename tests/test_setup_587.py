from services.completion_incident_classification import build_incident_classification, valid_incident_classification


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.87 TEST")
    print("============================================================")
    obj = build_incident_classification("sample", ["a", "b"], ["evidence"])
    assert valid_incident_classification(obj); print("[PASS] incident classification built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_incident_classification(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_incident_classification(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.87 tests complete.")

if __name__ == "__main__":
    main()
