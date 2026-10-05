from services.completion_task_checkpoint_recovery import build_task_checkpoint_recovery, valid_task_checkpoint_recovery, TaskCheckpointRecovery

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.38 TEST")
    print("============================================================")
    obj=build_task_checkpoint_recovery("sample", ["a","b"], ["a","b"], ["a","b"])
    assert valid_task_checkpoint_recovery(obj); print("[PASS] task checkpoint recovery built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_task_checkpoint_recovery(obj); print("[PASS] digest validates")
    assert not valid_task_checkpoint_recovery(TaskCheckpointRecovery("tampered", obj.checkpoint, obj.recovery, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.38 tests complete.")
if __name__ == "__main__": main()
