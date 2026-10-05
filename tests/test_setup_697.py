from services.completion_completion_evidence import build_completion_evidence, valid_completion_evidence, CompletionEvidence

def main():
    print("="*60); print("AZIZ AI SETUP 6.97 TEST"); print("="*60)
    obj=build_completion_evidence('sample', ['tests passed', 'runtime healthy'], ['task complete'], 'verified')
    assert valid_completion_evidence(obj); print("[PASS] completion evidence synthesis built")
    assert bool(obj.task_id) and bool(obj.evidence) and bool(obj.claims) and bool(obj.status); print("[PASS] contract data preserved")
    assert valid_completion_evidence(obj); print("[PASS] digest validates")
    tampered=CompletionEvidence("tampered", obj.evidence, obj.claims, obj.status, obj.digest)
    assert not valid_completion_evidence(tampered); print("[PASS] tamper rejected")
    print("Setup 6.97 tests complete.")

if __name__=="__main__": main()
