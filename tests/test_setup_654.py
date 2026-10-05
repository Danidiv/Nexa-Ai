from services.completion_runtime_behavior_verification import build_runtime_behavior_verification, valid_runtime_behavior_verification, RuntimeBehaviorVerification

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.54 TEST")
    print("============================================================")
    obj=build_runtime_behavior_verification("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_runtime_behavior_verification(obj); print("[PASS] runtime behavior verification built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_runtime_behavior_verification(obj); print("[PASS] digest validates")
    tampered=RuntimeBehaviorVerification("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_runtime_behavior_verification(tampered); print("[PASS] tamper rejected")
    print("Setup 6.54 tests complete.")

if __name__ == "__main__": main()
