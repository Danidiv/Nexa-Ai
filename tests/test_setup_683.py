from services.completion_task_file_targeting import build_task_file_targeting, valid_task_file_targeting, TaskFileTargeting

def main():
    print("="*60); print("AZIZ AI SETUP 6.83 TEST"); print("="*60)
    obj=build_task_file_targeting('sample', ['app.py', 'tests/test_app.py'], ['implementation', 'verification'])
    assert valid_task_file_targeting(obj); print("[PASS] task-to-file targeting built")
    assert bool(obj.task_id) and bool(obj.targets) and bool(obj.reasons); print("[PASS] contract data preserved")
    assert valid_task_file_targeting(obj); print("[PASS] digest validates")
    tampered=TaskFileTargeting("tampered", obj.targets, obj.reasons, obj.digest)
    assert not valid_task_file_targeting(tampered); print("[PASS] tamper rejected")
    print("Setup 6.83 tests complete.")

if __name__=="__main__": main()
