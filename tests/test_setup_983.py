from services.phase10_analytics_feature_planner import build_983, valid_983

def main():
    o=build_983("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"983"}, risk="low")
    assert valid_983(o) and o.valid() and o.setup=="983" and o.kind=="Analytics Feature Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_983(bad)
    try: build_983("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 983 Analytics Feature Planner")

if __name__=="__main__": main()
