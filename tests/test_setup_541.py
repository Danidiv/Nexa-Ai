import hashlib, json
from services.completion_visual_issue_clustering import build_visual_issue_clustering, valid_visual_issue_clustering

def run():
    print("="*60); print("AZIZ AI SETUP 5.541 TEST"); print("="*60)
    x=build_visual_issue_clustering(sample="ok", items=[1,2])
    assert x.payload["setup"]=="5.541"; print("[PASS] visual issue clustering built")
    assert x.payload["data"]["sample"]=="ok"; print("[PASS] contract data preserved")
    assert valid_visual_issue_clustering(x); print("[PASS] digest validates")
    tampered=type(x)(payload={**x.payload,"tampered":True},digest=x.digest)
    assert not valid_visual_issue_clustering(tampered); print("[PASS] tamper rejected")
    print("Setup 5.541 tests complete.")

if __name__=="__main__": run()
