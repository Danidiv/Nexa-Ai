from services.completion_dependency_risk_analysis import build_dependency_risk_analysis, valid_dependency_risk_analysis, DependencyRiskAnalysis

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.16 TEST")
    print("============================================================")
    obj=build_dependency_risk_analysis("sample",["a","b"],["evidence"]); assert valid_dependency_risk_analysis(obj); print("[PASS] dependency risk analysis built")
    assert obj.dependencies == ("a","b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_dependency_risk_analysis(obj); print("[PASS] digest validates")
    assert not valid_dependency_risk_analysis(DependencyRiskAnalysis(obj.name,("tampered",),obj.evidence,obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.16 tests complete.")
if __name__ == "__main__": main()
