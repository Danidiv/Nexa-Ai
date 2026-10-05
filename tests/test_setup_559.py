import copy
from services.completion_release_evidence import build_release_evidence, valid_release_evidence

def check(label, cond):
    if not cond: raise AssertionError(label)
    print("[PASS] "+label)

print("="*60)
print("AZIZ AI SETUP 5.59 TEST")
print("="*60)
c=build_release_evidence({"source":"qa","setup":"5.59"})
check("release evidence built", valid_release_evidence(c))
check("contract data preserved", c.payload["source"]=="qa")
check("digest validates", valid_release_evidence(c))
t=copy.deepcopy(c); object.__setattr__(t,"digest","0"*64)
check("tamper rejected", not valid_release_evidence(t))
print("Setup 5.59 tests complete.")
