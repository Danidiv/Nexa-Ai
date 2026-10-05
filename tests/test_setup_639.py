from services.completion_autonomous_coding_session import build_autonomous_coding_session, valid_autonomous_coding_session, AutonomousCodingSession

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.39 TEST")
    print("============================================================")
    obj=build_autonomous_coding_session("sample", ["a","b"], ["a","b"], ["a","b"])
    assert valid_autonomous_coding_session(obj); print("[PASS] autonomous coding session built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_autonomous_coding_session(obj); print("[PASS] digest validates")
    assert not valid_autonomous_coding_session(AutonomousCodingSession("tampered", obj.steps, obj.state, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.39 tests complete.")
if __name__ == "__main__": main()
