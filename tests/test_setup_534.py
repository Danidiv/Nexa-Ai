from services.completion_keyboard_flow import *

def check(x):
    assert x

r=inspect_keyboard([{"selector":"#save","focusable":True,"label":True}])
print("[PASS] keyboard elements inspected")
assert r["status"]=="pass"
print("[PASS] focus/label checks work")
assert valid_keyboard(r)
print("[PASS] keyboard digest validates")
r["elements"][0]["focusable"]=False
assert not valid_keyboard(r)
print("[PASS] tamper rejected")
