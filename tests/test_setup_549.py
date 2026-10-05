import hashlib, json
from services.completion_release_evidence_bundle import build_release_evidence_bundle, valid_release_evidence_bundle

def run():
    print("="*60); print("AZIZ AI SETUP 5.549 TEST"); print("="*60)
    x=build_release_evidence_bundle(sample="ok", items=[1,2])
    assert x.payload["setup"]=="5.549"; print("[PASS] release evidence bundle built")
    assert x.payload["data"]["sample"]=="ok"; print("[PASS] contract data preserved")
    assert valid_release_evidence_bundle(x); print("[PASS] digest validates")
    tampered=type(x)(payload={**x.payload,"tampered":True},digest=x.digest)
    assert not valid_release_evidence_bundle(tampered); print("[PASS] tamper rejected")
    print("Setup 5.549 tests complete.")

if __name__=="__main__": run()
