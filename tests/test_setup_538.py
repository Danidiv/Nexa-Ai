from services.completion_qa_repair_planner import *

def check(x):
    assert x

r=build_repair_plan([{"source":"contrast","status":"issues"},{"source":"network","status":"pass"}])
print("[PASS] QA repair plan built")
assert len(r["actions"])==1
print("[PASS] only failing evidence creates repair")
assert valid_repair_plan(r)
print("[PASS] repair digest validates")
r["actions"][0]["action"]="skip"
assert not valid_repair_plan(r)
print("[PASS] tamper rejected")
