from services.completion_network_health import *

def check(x):
    assert x

r=inspect_network([{"url":"/api","status":200,"duration_ms":120}])
print("[PASS] network requests inspected")
assert r["status"]=="pass"
print("[PASS] status/latency thresholds work")
assert valid_network(r)
print("[PASS] network digest validates")
r["requests"][0]["status"]=500
assert not valid_network(r)
print("[PASS] tamper rejected")
