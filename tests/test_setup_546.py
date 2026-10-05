import hashlib, json
from services.completion_browser_capability_matrix import build_browser_capability_matrix, valid_browser_capability_matrix

def run():
    print("="*60); print("AZIZ AI SETUP 5.546 TEST"); print("="*60)
    x=build_browser_capability_matrix(sample="ok", items=[1,2])
    assert x.payload["setup"]=="5.546"; print("[PASS] browser capability matrix built")
    assert x.payload["data"]["sample"]=="ok"; print("[PASS] contract data preserved")
    assert valid_browser_capability_matrix(x); print("[PASS] digest validates")
    tampered=type(x)(payload={**x.payload,"tampered":True},digest=x.digest)
    assert not valid_browser_capability_matrix(tampered); print("[PASS] tamper rejected")
    print("Setup 5.546 tests complete.")

if __name__=="__main__": run()
