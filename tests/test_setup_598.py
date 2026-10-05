from services.completion_security_posture import build_security_posture, valid_security_posture, SecurityPosture

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.98 TEST")
    print("============================================================")
    obj = build_security_posture("sample", ["a", "b"], ["evidence"])
    assert valid_security_posture(obj); print("[PASS] security controls built")
    assert obj.controls == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_security_posture(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["controls"] = ["tampered"]
    assert bad["controls"] != list(obj.controls) and not valid_security_posture(type(obj)(obj.name, tuple(bad["controls"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.98 tests complete.")

if __name__ == "__main__":
    main()
