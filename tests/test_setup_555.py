import copy
from services.completion_browser_matrix import build_browser_matrix, valid_browser_matrix

def check(label, cond):
    if not cond: raise AssertionError(label)
    print("[PASS] "+label)

print("="*60)
print("AZIZ AI SETUP 5.55 TEST")
print("="*60)
c=build_browser_matrix({"source":"qa","setup":"5.55"})
check("browser matrix built", valid_browser_matrix(c))
check("contract data preserved", c.payload["source"]=="qa")
check("digest validates", valid_browser_matrix(c))
t=copy.deepcopy(c); object.__setattr__(t,"digest","0"*64)
check("tamper rejected", not valid_browser_matrix(t))
print("Setup 5.55 tests complete.")
