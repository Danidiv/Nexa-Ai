import copy
from services.completion_repair_execution import build_repair_execution, valid_repair_execution

def check(label, cond):
    if not cond: raise AssertionError(label)
    print("[PASS] "+label)

print("="*60)
print("AZIZ AI SETUP 5.58 TEST")
print("="*60)
c=build_repair_execution({"source":"qa","setup":"5.58"})
check("repair execution built", valid_repair_execution(c))
check("contract data preserved", c.payload["source"]=="qa")
check("digest validates", valid_repair_execution(c))
t=copy.deepcopy(c); object.__setattr__(t,"digest","0"*64)
check("tamper rejected", not valid_repair_execution(t))
print("Setup 5.58 tests complete.")
