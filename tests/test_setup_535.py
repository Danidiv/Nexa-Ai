from services.completion_mobile_interaction import *

def check(x):
    assert x

r=inspect_mobile([{"selector":"button","width":48,"height":48}])
print("[PASS] mobile targets inspected")
assert r["status"]=="pass"
print("[PASS] tap target threshold works")
assert valid_mobile(r)
print("[PASS] mobile digest validates")
r["targets"][0]["width"]=10
assert not valid_mobile(r)
print("[PASS] tamper rejected")
