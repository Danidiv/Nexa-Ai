from services.completion_task_state_persistence import build_task_state_persistence, valid_task_state_persistence, TaskStatePersistence

def main():
    print("="*60); print("AZIZ AI SETUP 6.73 TEST"); print("="*60)
    obj=build_task_state_persistence("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_task_state_persistence(obj); print("[PASS] task state persistence built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_task_state_persistence(obj); print("[PASS] digest validates")
    tampered=TaskStatePersistence("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_task_state_persistence(tampered); print("[PASS] tamper rejected")
    print("Setup 6.73 tests complete.")

if __name__=="__main__": main()
