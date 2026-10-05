import hashlib, json
from services.completion_release_readiness_agent import build_release_readiness_agent, valid_release_readiness_agent

def run():
    print("="*60); print("AZIZ AI SETUP 5.550 TEST"); print("="*60)
    x=build_release_readiness_agent(sample="ok", items=[1,2])
    assert x.payload["setup"]=="5.550"; print("[PASS] release readiness agent built")
    assert x.payload["data"]["sample"]=="ok"; print("[PASS] contract data preserved")
    assert valid_release_readiness_agent(x); print("[PASS] digest validates")
    tampered=type(x)(payload={**x.payload,"tampered":True},digest=x.digest)
    assert not valid_release_readiness_agent(tampered); print("[PASS] tamper rejected")
    print("Setup 5.550 tests complete.")

if __name__=="__main__": run()
