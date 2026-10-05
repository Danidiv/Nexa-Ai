from services.completion_performance_regression_analysis import build_performance_regression_analysis, valid_performance_regression_analysis, PerformanceRegressionAnalysis

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.17 TEST")
    print("============================================================")
    obj=build_performance_regression_analysis("sample",["a","b"],["evidence"]); assert valid_performance_regression_analysis(obj); print("[PASS] performance regression analysis built")
    assert obj.benchmarks == ("a","b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_performance_regression_analysis(obj); print("[PASS] digest validates")
    assert not valid_performance_regression_analysis(PerformanceRegressionAnalysis(obj.name,("tampered",),obj.evidence,obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.17 tests complete.")
if __name__ == "__main__": main()
