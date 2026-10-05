import copy
from services.completion_capability_selection import build_capability_selection, valid_capability_selection

def check(label, cond):
    if not cond: raise AssertionError(label)
    print("[PASS] "+label)

print("="*60)
print("AZIZ AI SETUP 5.56 TEST")
print("="*60)
c=build_capability_selection({"source":"qa","setup":"5.56"})
check("capability selection built", valid_capability_selection(c))
check("contract data preserved", c.payload["source"]=="qa")
check("digest validates", valid_capability_selection(c))
t=copy.deepcopy(c); object.__setattr__(t,"digest","0"*64)
check("tamper rejected", not valid_capability_selection(t))
print("Setup 5.56 tests complete.")
