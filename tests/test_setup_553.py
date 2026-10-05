import copy
from services.completion_baseline_comparison import build_baseline_comparison, valid_baseline_comparison

def check(label, cond):
    if not cond: raise AssertionError(label)
    print("[PASS] "+label)

print("="*60)
print("AZIZ AI SETUP 5.53 TEST")
print("="*60)
c=build_baseline_comparison({"source":"qa","setup":"5.53"})
check("baseline comparison built", valid_baseline_comparison(c))
check("contract data preserved", c.payload["source"]=="qa")
check("digest validates", valid_baseline_comparison(c))
t=copy.deepcopy(c); object.__setattr__(t,"digest","0"*64)
check("tamper rejected", not valid_baseline_comparison(t))
print("Setup 5.53 tests complete.")
