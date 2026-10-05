from services.completion_repair_candidates import build_repair_candidates, valid_repair_candidates, RepairCandidates

def main():
    print("="*60); print("AZIZ AI SETUP 6.91 TEST"); print("="*60)
    obj=build_repair_candidates('sample', ['fix return'], [0.9], ['root cause'])
    assert valid_repair_candidates(obj); print("[PASS] repair candidate generation built")
    assert bool(obj.task_id) and bool(obj.candidates) and bool(obj.scores) and bool(obj.basis); print("[PASS] contract data preserved")
    assert valid_repair_candidates(obj); print("[PASS] digest validates")
    tampered=RepairCandidates("tampered", obj.candidates, obj.scores, obj.basis, obj.digest)
    assert not valid_repair_candidates(tampered); print("[PASS] tamper rejected")
    print("Setup 6.91 tests complete.")

if __name__=="__main__": main()
