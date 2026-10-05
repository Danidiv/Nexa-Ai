from services.completion_session_summary import build_session_summary, valid_session_summary, SessionSummary

def main():
    print("="*60); print("AZIZ AI SETUP 6.78 TEST"); print("="*60)
    obj=build_session_summary("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_session_summary(obj); print("[PASS] engineering session summary built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_session_summary(obj); print("[PASS] digest validates")
    tampered=SessionSummary("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_session_summary(tampered); print("[PASS] tamper rejected")
    print("Setup 6.78 tests complete.")

if __name__=="__main__": main()
