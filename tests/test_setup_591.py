from services.completion_incident_response import build_incident_response, valid_incident_response, IncidentResponse

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.91 TEST")
    print("============================================================")
    obj = build_incident_response("sample", ["a", "b"], ["evidence"])
    assert valid_incident_response(obj); print("[PASS] response evidence built")
    assert obj.steps == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_incident_response(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["steps"] = ["tampered"]
    assert bad["steps"] != list(obj.steps) and not valid_incident_response(type(obj)(obj.name, tuple(bad["steps"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.91 tests complete.")

if __name__ == "__main__":
    main()
