from services.completion_regression_test_selection import build_regression_test_selection, valid_regression_test_selection, RegressionTestSelection

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.53 TEST")
    print("============================================================")
    obj=build_regression_test_selection("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_regression_test_selection(obj); print("[PASS] regression test selection built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_regression_test_selection(obj); print("[PASS] digest validates")
    tampered=RegressionTestSelection("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_regression_test_selection(tampered); print("[PASS] tamper rejected")
    print("Setup 6.53 tests complete.")

if __name__ == "__main__": main()
