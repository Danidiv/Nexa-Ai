from services.completion_human_escalation import build_human_escalation, valid_human_escalation, HumanEscalation

def main():
    print("="*60); print("AZIZ AI SETUP 6.75 TEST"); print("="*60)
    obj=build_human_escalation("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_human_escalation(obj); print("[PASS] human escalation built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_human_escalation(obj); print("[PASS] digest validates")
    tampered=HumanEscalation("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_human_escalation(tampered); print("[PASS] tamper rejected")
    print("Setup 6.75 tests complete.")

if __name__=="__main__": main()
