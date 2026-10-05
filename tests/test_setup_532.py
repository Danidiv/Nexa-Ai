from services.completion_ux_semantics import *

def check(x):
    assert x

r=inspect_ux("<html><head><title>X</title></head><body><nav></nav><main><h1>X</h1></main></body></html>")
print("[PASS] UX semantics inspected")
assert r["status"]=="pass"
print("[PASS] semantic landmarks pass")
assert valid_ux(r)
print("[PASS] UX digest validates")
r["checks"]["nav"]=False
assert not valid_ux(r)
print("[PASS] tamper rejected")
