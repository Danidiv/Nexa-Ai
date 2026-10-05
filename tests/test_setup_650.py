from services.completion_root_cause_confidence import build_root_cause_confidence, valid_root_cause_confidence, RootCauseConfidence

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.50 TEST")
    print("============================================================")
    obj=build_root_cause_confidence("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_root_cause_confidence(obj); print("[PASS] root cause confidence built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_root_cause_confidence(obj); print("[PASS] digest validates")
    tampered=RootCauseConfidence("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_root_cause_confidence(tampered); print("[PASS] tamper rejected")
    print("Setup 6.50 tests complete.")

if __name__ == "__main__": main()
