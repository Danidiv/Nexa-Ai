from services.completion_patch_risk_assessment import build_patch_risk_assessment, valid_patch_risk_assessment, PatchRiskAssessment

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.11 TEST")
    print("============================================================")
    obj=build_patch_risk_assessment("sample",["a","b"],["evidence"]); assert valid_patch_risk_assessment(obj); print("[PASS] patch risk assessment built")
    assert obj.risks == ("a","b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_patch_risk_assessment(obj); print("[PASS] digest validates")
    assert not valid_patch_risk_assessment(PatchRiskAssessment(obj.name,("tampered",),obj.evidence,obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.11 tests complete.")
if __name__ == "__main__": main()
