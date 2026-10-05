from services.completion_test_prioritization import build_test_prioritization, valid_test_prioritization, TestPrioritization

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.48 TEST")
    print("============================================================")
    obj=build_test_prioritization("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_test_prioritization(obj); print("[PASS] test prioritization built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_test_prioritization(obj); print("[PASS] digest validates")
    tampered=TestPrioritization("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_test_prioritization(tampered); print("[PASS] tamper rejected")
    print("Setup 6.48 tests complete.")

if __name__ == "__main__": main()
