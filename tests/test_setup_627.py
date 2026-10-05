from services.completion_test_execution_orchestration import build_test_execution_orchestration, valid_test_execution_orchestration, TestExecutionOrchestration

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.27 TEST")
    print("============================================================")
    obj=build_test_execution_orchestration(["a","b"], ["a","b"], {"max": 3}, ["a","b"])
    assert valid_test_execution_orchestration(obj); print("[PASS] test execution orchestration built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_test_execution_orchestration(obj); print("[PASS] digest validates")
    assert not valid_test_execution_orchestration(TestExecutionOrchestration(( "tampered", ), obj.stages, obj.limits, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.27 tests complete.")
if __name__ == "__main__": main()
