from services.completion_long_running_checkpoint import build_long_running_checkpoint, valid_long_running_checkpoint, LongRunningCheckpoint

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.18 TEST")
    print("============================================================")
    obj=build_long_running_checkpoint("sample",["a","b"],["evidence"]); assert valid_long_running_checkpoint(obj); print("[PASS] long-running task checkpoint built")
    assert obj.checkpoints == ("a","b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_long_running_checkpoint(obj); print("[PASS] digest validates")
    assert not valid_long_running_checkpoint(LongRunningCheckpoint(obj.name,("tampered",),obj.evidence,obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.18 tests complete.")
if __name__ == "__main__": main()
