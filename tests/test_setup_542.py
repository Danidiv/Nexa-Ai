import hashlib, json
from services.completion_ux_flow_scoring import build_ux_flow_scoring, valid_ux_flow_scoring

def run():
    print("="*60); print("AZIZ AI SETUP 5.542 TEST"); print("="*60)
    x=build_ux_flow_scoring(sample="ok", items=[1,2])
    assert x.payload["setup"]=="5.542"; print("[PASS] ux flow scoring built")
    assert x.payload["data"]["sample"]=="ok"; print("[PASS] contract data preserved")
    assert valid_ux_flow_scoring(x); print("[PASS] digest validates")
    tampered=type(x)(payload={**x.payload,"tampered":True},digest=x.digest)
    assert not valid_ux_flow_scoring(tampered); print("[PASS] tamper rejected")
    print("Setup 5.542 tests complete.")

if __name__=="__main__": run()
