from services.completion_repository_task_intake import build_repository_task_intake, valid_repository_task_intake, RepositoryTaskIntake

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.41 TEST")
    print("============================================================")
    obj=build_repository_task_intake("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_repository_task_intake(obj); print("[PASS] repository task intake built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_repository_task_intake(obj); print("[PASS] digest validates")
    tampered=RepositoryTaskIntake("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_repository_task_intake(tampered); print("[PASS] tamper rejected")
    print("Setup 6.41 tests complete.")

if __name__ == "__main__": main()
