from services.completion_autonomous_coding_runtime import build_autonomous_coding_runtime, valid_autonomous_coding_runtime, AutonomousCodingRuntime

def main():
    print("="*60); print("AZIZ AI SETUP 6.80 TEST"); print("="*60)
    obj=build_autonomous_coding_runtime("sample", ["understand","plan","modify","verify"], ["app.py"], ["tests"], ["verified"], "completed")
    assert valid_autonomous_coding_runtime(obj); print("[PASS] integrated autonomous coding runtime built")
    assert obj.phases and obj.changed_files and obj.tests and obj.evidence; print("[PASS] runtime data preserved")
    assert valid_autonomous_coding_runtime(obj); print("[PASS] digest validates")
    tampered=AutonomousCodingRuntime("tampered", obj.phases, obj.changed_files, obj.tests, obj.evidence, obj.status, obj.digest)
    assert not valid_autonomous_coding_runtime(tampered); print("[PASS] tamper rejected")
    print("Setup 6.80 tests complete.")

if __name__=="__main__": main()
