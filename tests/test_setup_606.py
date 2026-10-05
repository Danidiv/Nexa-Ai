from services.completion_test_execution_matrix import build_test_execution_matrix, valid_test_execution_matrix, TestExecutionMatrix

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.06 TEST")
    print("============================================================")
    obj = build_test_execution_matrix("sample", ["a", "b"], ["evidence"])
    assert valid_test_execution_matrix(obj); print("[PASS] test execution matrix built")
    assert obj.runs == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_test_execution_matrix(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["runs"] = ["tampered"]
    assert not valid_test_execution_matrix(TestExecutionMatrix(obj.name, tuple(bad["runs"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.06 tests complete.")

if __name__ == "__main__":
    main()
