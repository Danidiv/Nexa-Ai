from services.phase9_903_authentication_flow_planner import build_903,valid_903

def main():
    o=build_903("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.03","goal":"saas"},risk="low")
    assert valid_903(o) and o.valid() and o.setup=="9.03" and o.kind=="Authentication Flow Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_903(bad)
    try: build_903("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.03 Authentication Flow Planner")

if __name__=="__main__": main()
