from services.completion_regression_guard import build_regression_guard, valid_regression_guard, RegressionGuard

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.30 TEST")
    print("============================================================")
    obj=build_regression_guard(["a","b"], ["a","b"], {"max": 3}, ["a","b"])
    assert valid_regression_guard(obj); print("[PASS] regression guard built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_regression_guard(obj); print("[PASS] digest validates")
    assert not valid_regression_guard(RegressionGuard(( "tampered", ), obj.checks, obj.thresholds, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.30 tests complete.")
if __name__ == "__main__": main()
