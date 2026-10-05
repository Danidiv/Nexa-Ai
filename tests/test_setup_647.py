from services.completion_command_safety import build_command_safety, valid_command_safety, CommandSafety

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.47 TEST")
    print("============================================================")
    obj=build_command_safety("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_command_safety(obj); print("[PASS] command safety built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_command_safety(obj); print("[PASS] digest validates")
    tampered=CommandSafety("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_command_safety(tampered); print("[PASS] tamper rejected")
    print("Setup 6.47 tests complete.")

if __name__ == "__main__": main()
