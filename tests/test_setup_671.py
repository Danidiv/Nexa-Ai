from services.completion_verification_gate import build_verification_gate, valid_verification_gate, VerificationGate

def main():
    print("="*60); print("AZIZ AI SETUP 6.71 TEST"); print("="*60)
    obj=build_verification_gate("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_verification_gate(obj); print("[PASS] verification gate built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_verification_gate(obj); print("[PASS] digest validates")
    tampered=VerificationGate("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_verification_gate(tampered); print("[PASS] tamper rejected")
    print("Setup 6.71 tests complete.")

if __name__=="__main__": main()
