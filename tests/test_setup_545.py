import hashlib, json
from services.completion_cross_browser_matrix import build_cross_browser_matrix, valid_cross_browser_matrix

def run():
    print("="*60); print("AZIZ AI SETUP 5.545 TEST"); print("="*60)
    x=build_cross_browser_matrix(sample="ok", items=[1,2])
    assert x.payload["setup"]=="5.545"; print("[PASS] cross-browser matrix built")
    assert x.payload["data"]["sample"]=="ok"; print("[PASS] contract data preserved")
    assert valid_cross_browser_matrix(x); print("[PASS] digest validates")
    tampered=type(x)(payload={**x.payload,"tampered":True},digest=x.digest)
    assert not valid_cross_browser_matrix(tampered); print("[PASS] tamper rejected")
    print("Setup 5.545 tests complete.")

if __name__=="__main__": run()
