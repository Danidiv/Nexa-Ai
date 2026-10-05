from services.completion_interruption_recovery import build_interruption_recovery, valid_interruption_recovery, InterruptionRecovery

def main():
    print("="*60); print("AZIZ AI SETUP 6.74 TEST"); print("="*60)
    obj=build_interruption_recovery("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_interruption_recovery(obj); print("[PASS] interruption recovery built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_interruption_recovery(obj); print("[PASS] digest validates")
    tampered=InterruptionRecovery("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_interruption_recovery(tampered); print("[PASS] tamper rejected")
    print("Setup 6.74 tests complete.")

if __name__=="__main__": main()
