from services.completion_failure_classification import build_failure_classification, valid_failure_classification, FailureClassification

def main():
    print("="*60); print("AZIZ AI SETUP 6.89 TEST"); print("="*60)
    obj=build_failure_classification('sample', ['assertion failed'], ['test_failure'], ['high'])
    assert valid_failure_classification(obj); print("[PASS] failure classification built")
    assert bool(obj.task_id) and bool(obj.failures) and bool(obj.classes) and bool(obj.severity); print("[PASS] contract data preserved")
    assert valid_failure_classification(obj); print("[PASS] digest validates")
    tampered=FailureClassification("tampered", obj.failures, obj.classes, obj.severity, obj.digest)
    assert not valid_failure_classification(tampered); print("[PASS] tamper rejected")
    print("Setup 6.89 tests complete.")

if __name__=="__main__": main()
