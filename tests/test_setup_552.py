import copy
from services.completion_ux_risk_scoring import build_ux_risk_scoring, valid_ux_risk_scoring

def check(label, cond):
    if not cond: raise AssertionError(label)
    print("[PASS] "+label)

print("="*60)
print("AZIZ AI SETUP 5.52 TEST")
print("="*60)
c=build_ux_risk_scoring({"source":"qa","setup":"5.52"})
check("ux risk scoring built", valid_ux_risk_scoring(c))
check("contract data preserved", c.payload["source"]=="qa")
check("digest validates", valid_ux_risk_scoring(c))
t=copy.deepcopy(c); object.__setattr__(t,"digest","0"*64)
check("tamper rejected", not valid_ux_risk_scoring(t))
print("Setup 5.52 tests complete.")
