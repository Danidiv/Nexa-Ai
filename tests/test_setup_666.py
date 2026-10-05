from services.completion_test_execution_record import build_test_execution_record, valid_test_execution_record, TestExecutionRecord

def main():
    print("="*60); print("AZIZ AI SETUP 6.66 TEST"); print("="*60)
    obj=build_test_execution_record("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_test_execution_record(obj); print("[PASS] test execution record built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_test_execution_record(obj); print("[PASS] digest validates")
    tampered=TestExecutionRecord("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_test_execution_record(tampered); print("[PASS] tamper rejected")
    print("Setup 6.66 tests complete.")

if __name__=="__main__": main()
