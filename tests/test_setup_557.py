import copy
from services.completion_artifact_lineage import build_artifact_lineage, valid_artifact_lineage

def check(label, cond):
    if not cond: raise AssertionError(label)
    print("[PASS] "+label)

print("="*60)
print("AZIZ AI SETUP 5.57 TEST")
print("="*60)
c=build_artifact_lineage({"source":"qa","setup":"5.57"})
check("artifact lineage built", valid_artifact_lineage(c))
check("contract data preserved", c.payload["source"]=="qa")
check("digest validates", valid_artifact_lineage(c))
t=copy.deepcopy(c); object.__setattr__(t,"digest","0"*64)
check("tamper rejected", not valid_artifact_lineage(t))
print("Setup 5.57 tests complete.")
