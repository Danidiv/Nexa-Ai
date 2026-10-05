from services.completion_user_visible_behavior_verification import build_user_visible_behavior_verification, valid_user_visible_behavior_verification, UserVisibleBehaviorVerification

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.55 TEST")
    print("============================================================")
    obj=build_user_visible_behavior_verification("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_user_visible_behavior_verification(obj); print("[PASS] user-visible behavior verification built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_user_visible_behavior_verification(obj); print("[PASS] digest validates")
    tampered=UserVisibleBehaviorVerification("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_user_visible_behavior_verification(tampered); print("[PASS] tamper rejected")
    print("Setup 6.55 tests complete.")

if __name__ == "__main__": main()
