import hashlib, json
from services.completion_visual_approval import build_visual_approval, valid_visual_approval

def run():
    print("="*60); print("AZIZ AI SETUP 5.544 TEST"); print("="*60)
    x=build_visual_approval(sample="ok", items=[1,2])
    assert x.payload["setup"]=="5.544"; print("[PASS] visual approval gate built")
    assert x.payload["data"]["sample"]=="ok"; print("[PASS] contract data preserved")
    assert valid_visual_approval(x); print("[PASS] digest validates")
    tampered=type(x)(payload={**x.payload,"tampered":True},digest=x.digest)
    assert not valid_visual_approval(tampered); print("[PASS] tamper rejected")
    print("Setup 5.544 tests complete.")

if __name__=="__main__": run()
