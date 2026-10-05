from services.completion_regression_analysis import build_regression_analysis, valid_regression_analysis, RegressionAnalysis

def main():
    print("="*60); print("AZIZ AI SETUP 6.95 TEST"); print("="*60)
    obj=build_regression_analysis('sample', ['auth'], ['test_auth.py'], ['no regression'])
    assert valid_regression_analysis(obj); print("[PASS] regression analysis built")
    assert bool(obj.task_id) and bool(obj.areas) and bool(obj.tests) and bool(obj.findings); print("[PASS] contract data preserved")
    assert valid_regression_analysis(obj); print("[PASS] digest validates")
    tampered=RegressionAnalysis("tampered", obj.areas, obj.tests, obj.findings, obj.digest)
    assert not valid_regression_analysis(tampered); print("[PASS] tamper rejected")
    print("Setup 6.95 tests complete.")

if __name__=="__main__": main()
