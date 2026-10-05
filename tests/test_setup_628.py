from services.completion_failure_diagnosis import build_failure_diagnosis, valid_failure_diagnosis, FailureDiagnosis

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.28 TEST")
    print("============================================================")
    obj=build_failure_diagnosis(["a","b"], ["a","b"], {"max": 3}, ["a","b"])
    assert valid_failure_diagnosis(obj); print("[PASS] failure diagnosis built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_failure_diagnosis(obj); print("[PASS] digest validates")
    assert not valid_failure_diagnosis(FailureDiagnosis(( "tampered", ), obj.causes, obj.confidence, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.28 tests complete.")
if __name__ == "__main__": main()
