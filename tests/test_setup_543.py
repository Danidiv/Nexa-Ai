import hashlib, json
from services.completion_visual_baseline_registry import build_visual_baseline_registry, valid_visual_baseline_registry

def run():
    print("="*60); print("AZIZ AI SETUP 5.543 TEST"); print("="*60)
    x=build_visual_baseline_registry(sample="ok", items=[1,2])
    assert x.payload["setup"]=="5.543"; print("[PASS] visual baseline registry built")
    assert x.payload["data"]["sample"]=="ok"; print("[PASS] contract data preserved")
    assert valid_visual_baseline_registry(x); print("[PASS] digest validates")
    tampered=type(x)(payload={**x.payload,"tampered":True},digest=x.digest)
    assert not valid_visual_baseline_registry(tampered); print("[PASS] tamper rejected")
    print("Setup 5.543 tests complete.")

if __name__=="__main__": run()
