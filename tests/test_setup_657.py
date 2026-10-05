from services.completion_engineering_decision_log import build_engineering_decision_log, valid_engineering_decision_log, EngineeringDecisionLog

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.57 TEST")
    print("============================================================")
    obj=build_engineering_decision_log("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_engineering_decision_log(obj); print("[PASS] engineering decision log built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_engineering_decision_log(obj); print("[PASS] digest validates")
    tampered=EngineeringDecisionLog("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_engineering_decision_log(tampered); print("[PASS] tamper rejected")
    print("Setup 6.57 tests complete.")

if __name__ == "__main__": main()
