from services.completion_visual_qa_orchestrator import *

def check(x):
    assert x

html="<html><head><title>X</title></head><body><nav></nav><main><h1>X</h1></main></body></html>"
r=orchestrate("http://local",html,"abc","abc",{"load_ms":100})
print("[PASS] full visual QA orchestration validates")
assert r["status"]=="ready"
print("[PASS] QA/repair/release layers integrated")
assert valid_orchestration(r)
print("[PASS] orchestration digest validates")
r["gate"]["status"]="blocked"
assert not valid_orchestration(r)
print("[PASS] tampered orchestration rejected")
