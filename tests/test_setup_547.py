import hashlib, json
from services.completion_test_artifact_registry import build_test_artifact_registry, valid_test_artifact_registry

def run():
    print("="*60); print("AZIZ AI SETUP 5.547 TEST"); print("="*60)
    x=build_test_artifact_registry(sample="ok", items=[1,2])
    assert x.payload["setup"]=="5.547"; print("[PASS] test artifact registry built")
    assert x.payload["data"]["sample"]=="ok"; print("[PASS] contract data preserved")
    assert valid_test_artifact_registry(x); print("[PASS] digest validates")
    tampered=type(x)(payload={**x.payload,"tampered":True},digest=x.digest)
    assert not valid_test_artifact_registry(tampered); print("[PASS] tamper rejected")
    print("Setup 5.547 tests complete.")

if __name__=="__main__": run()
