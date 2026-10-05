from services.completion_autonomous_stop_conditions import build_autonomous_stop_conditions, valid_autonomous_stop_conditions, AutonomousStopConditions

def main():
    print("="*60); print("AZIZ AI SETUP 6.76 TEST"); print("="*60)
    obj=build_autonomous_stop_conditions("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_autonomous_stop_conditions(obj); print("[PASS] autonomous stop conditions built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_autonomous_stop_conditions(obj); print("[PASS] digest validates")
    tampered=AutonomousStopConditions("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_autonomous_stop_conditions(tampered); print("[PASS] tamper rejected")
    print("Setup 6.76 tests complete.")

if __name__=="__main__": main()
