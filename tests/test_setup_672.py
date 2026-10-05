from services.completion_evidence_collector import build_evidence_collector, valid_evidence_collector, EvidenceCollector

def main():
    print("="*60); print("AZIZ AI SETUP 6.72 TEST"); print("="*60)
    obj=build_evidence_collector("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_evidence_collector(obj); print("[PASS] evidence collector built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_evidence_collector(obj); print("[PASS] digest validates")
    tampered=EvidenceCollector("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_evidence_collector(tampered); print("[PASS] tamper rejected")
    print("Setup 6.72 tests complete.")

if __name__=="__main__": main()
