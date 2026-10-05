from services.completion_test_selection import build_test_selection, valid_test_selection, TestSelection

def main():
    print("="*60); print("AZIZ AI SETUP 6.88 TEST"); print("="*60)
    obj=build_test_selection('sample', ['test_app.py'], ['high'], ['covers changed file'])
    assert valid_test_selection(obj); print("[PASS] test selection built")
    assert bool(obj.task_id) and bool(obj.tests) and bool(obj.priorities) and bool(obj.reasons); print("[PASS] contract data preserved")
    assert valid_test_selection(obj); print("[PASS] digest validates")
    tampered=TestSelection("tampered", obj.tests, obj.priorities, obj.reasons, obj.digest)
    assert not valid_test_selection(tampered); print("[PASS] tamper rejected")
    print("Setup 6.88 tests complete.")

if __name__=="__main__": main()
