import copy
from services.completion_approval_policy import build_approval_policy, valid_approval_policy

def check(label, cond):
    if not cond: raise AssertionError(label)
    print("[PASS] "+label)

print("="*60)
print("AZIZ AI SETUP 5.54 TEST")
print("="*60)
c=build_approval_policy({"source":"qa","setup":"5.54"})
check("approval policy built", valid_approval_policy(c))
check("contract data preserved", c.payload["source"]=="qa")
check("digest validates", valid_approval_policy(c))
t=copy.deepcopy(c); object.__setattr__(t,"digest","0"*64)
check("tamper rejected", not valid_approval_policy(t))
print("Setup 5.54 tests complete.")
