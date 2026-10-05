from services.phase8_888_feature_retirement_planner import build_888,valid_888
def main():
    o=build_888("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_888(o) and o.valid() and o.setup=="8.88" and o.kind=="Feature Retirement Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_888(bad)
    try: build_888("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.88 Feature Retirement Planner")
if __name__=="__main__": main()
