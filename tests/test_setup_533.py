from services.completion_color_contrast import *

def check(x):
    assert x

r=inspect_contrast([{"name":"body","ratio":7.1},{"name":"muted","ratio":4.6}])
print("[PASS] contrast samples inspected")
assert r["status"]=="pass"
print("[PASS] AA/AAA thresholds work")
assert valid_contrast(r)
print("[PASS] contrast digest validates")
r["samples"][0]["ratio"]=1
assert not valid_contrast(r)
print("[PASS] tamper rejected")
