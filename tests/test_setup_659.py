from services.completion_autonomous_task_memory import build_autonomous_task_memory, valid_autonomous_task_memory, AutonomousTaskMemory

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.59 TEST")
    print("============================================================")
    obj=build_autonomous_task_memory("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_autonomous_task_memory(obj); print("[PASS] autonomous task memory built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_autonomous_task_memory(obj); print("[PASS] digest validates")
    tampered=AutonomousTaskMemory("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_autonomous_task_memory(tampered); print("[PASS] tamper rejected")
    print("Setup 6.59 tests complete.")

if __name__ == "__main__": main()
