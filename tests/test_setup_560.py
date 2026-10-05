import copy
from services.completion_release_readiness import build_release_readiness, valid_release_readiness

def check(label, cond):
    if not cond: raise AssertionError(label)
    print("[PASS] "+label)

print("="*60)
print("AZIZ AI SETUP 5.60 TEST")
print("="*60)
c=build_release_readiness({"source":"qa","setup":"5.60"})
check("release readiness built", valid_release_readiness(c))
check("contract data preserved", c.payload["source"]=="qa")
check("digest validates", valid_release_readiness(c))
t=copy.deepcopy(c); object.__setattr__(t,"digest","0"*64)
check("tamper rejected", not valid_release_readiness(t))
print("Setup 5.60 tests complete.")
