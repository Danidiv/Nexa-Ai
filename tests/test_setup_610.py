from services.completion_autonomous_debugging_loop import build_autonomous_debugging_loop, valid_autonomous_debugging_loop, AutonomousDebuggingLoop

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.10 TEST")
    print("============================================================")
    obj=build_autonomous_debugging_loop("sample",["a","b"],["evidence"]); assert valid_autonomous_debugging_loop(obj); print("[PASS] autonomous debugging loop built")
    assert obj.stages == ("a","b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_autonomous_debugging_loop(obj); print("[PASS] digest validates")
    assert not valid_autonomous_debugging_loop(AutonomousDebuggingLoop(obj.name,("tampered",),obj.evidence,obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.10 tests complete.")
if __name__ == "__main__": main()
