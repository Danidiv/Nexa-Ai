from services.completion_flaky_detection import *

def check(x):
    assert x

r=detect_flaky([{"name":"a","status":"pass"},{"name":"a","status":"fail"}])
print("[PASS] test history grouped")
assert r["status"]=="flaky"
print("[PASS] flaky pattern detected")
assert valid_flaky(r)
print("[PASS] flaky digest validates")
r["tests"][0]["flaky"]=False
assert not valid_flaky(r)
print("[PASS] tamper rejected")
