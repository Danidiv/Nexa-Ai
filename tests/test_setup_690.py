from services.completion_root_cause_evidence import build_root_cause_evidence, valid_root_cause_evidence, RootCauseEvidence

def main():
    print("="*60); print("AZIZ AI SETUP 6.90 TEST"); print("="*60)
    obj=build_root_cause_evidence('sample', ['bad return'], ['traceback line 4'], [0.9])
    assert valid_root_cause_evidence(obj); print("[PASS] root cause evidence built")
    assert bool(obj.task_id) and bool(obj.causes) and bool(obj.evidence) and bool(obj.confidence); print("[PASS] contract data preserved")
    assert valid_root_cause_evidence(obj); print("[PASS] digest validates")
    tampered=RootCauseEvidence("tampered", obj.causes, obj.evidence, obj.confidence, obj.digest)
    assert not valid_root_cause_evidence(tampered); print("[PASS] tamper rejected")
    print("Setup 6.90 tests complete.")

if __name__=="__main__": main()
