from services.completion_release_gate import *

def check(x):
    assert x

r=evaluate_release([{"name":"visual","status":"pass"},{"name":"flaky","status":"stable"}])
print("[PASS] release gate evaluated")
assert r["status"]=="ready"
print("[PASS] ready state works")
assert valid_release(r)
print("[PASS] release digest validates")
r["checks"][0]["status"]="issues"
assert not valid_release(r)
print("[PASS] tamper rejected")
