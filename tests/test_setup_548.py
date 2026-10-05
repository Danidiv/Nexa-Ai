import hashlib, json
from services.completion_qa_repair_execution import build_qa_repair_execution, valid_qa_repair_execution

def run():
    print("="*60); print("AZIZ AI SETUP 5.548 TEST"); print("="*60)
    x=build_qa_repair_execution(sample="ok", items=[1,2])
    assert x.payload["setup"]=="5.548"; print("[PASS] qa repair execution built")
    assert x.payload["data"]["sample"]=="ok"; print("[PASS] contract data preserved")
    assert valid_qa_repair_execution(x); print("[PASS] digest validates")
    tampered=type(x)(payload={**x.payload,"tampered":True},digest=x.digest)
    assert not valid_qa_repair_execution(tampered); print("[PASS] tamper rejected")
    print("Setup 5.548 tests complete.")

if __name__=="__main__": run()
