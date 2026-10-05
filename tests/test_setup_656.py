from services.completion_task_progress_tracking import build_task_progress_tracking, valid_task_progress_tracking, TaskProgressTracking

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.56 TEST")
    print("============================================================")
    obj=build_task_progress_tracking("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_task_progress_tracking(obj); print("[PASS] task progress tracking built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_task_progress_tracking(obj); print("[PASS] digest validates")
    tampered=TaskProgressTracking("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_task_progress_tracking(tampered); print("[PASS] tamper rejected")
    print("Setup 6.56 tests complete.")

if __name__ == "__main__": main()
