from services.completion_regression_loop import build_regression_loop, valid_regression_loop

def main():
    obj=build_regression_loop("sample", **{f: [f"sample-{f}"] for f in ['repair', 'tests', 'regressions']})
    assert valid_regression_loop(obj)
    assert obj.kind == "regression_loop"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.43 Regression Repair Loop")

if __name__=="__main__": main()
