import copy
from services.completion_visual_issue_deduplication import build_visual_issue_deduplication, valid_visual_issue_deduplication

def check(label, cond):
    if not cond: raise AssertionError(label)
    print("[PASS] "+label)

print("="*60)
print("AZIZ AI SETUP 5.51 TEST")
print("="*60)
c=build_visual_issue_deduplication({"source":"qa","setup":"5.51"})
check("visual issue deduplication built", valid_visual_issue_deduplication(c))
check("contract data preserved", c.payload["source"]=="qa")
check("digest validates", valid_visual_issue_deduplication(c))
t=copy.deepcopy(c); object.__setattr__(t,"digest","0"*64)
check("tamper rejected", not valid_visual_issue_deduplication(t))
print("Setup 5.51 tests complete.")
