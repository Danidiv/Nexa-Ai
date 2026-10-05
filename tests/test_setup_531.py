from services.completion_visual_issue_prioritization import *

def check(x):
    assert x

r=prioritize([{"id":"a","severity":"low","category":"layout"},{"id":"b","severity":"critical","category":"a11y"}])
print("[PASS] visual issues prioritized")
assert r["issues"][0]["id"]=="b"
print("[PASS] critical issue ranked first")
assert valid_priorities(r)
print("[PASS] priority digest validates")
r["issues"][0]["severity"]="low"
assert not valid_priorities(r)
print("[PASS] tamper rejected")
