from services.phase9_930_external_integration_planner import build_930,valid_930

def main():
    o=build_930("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.30","goal":"saas"},risk="low")
    assert valid_930(o) and o.valid() and o.setup=="9.30" and o.kind=="External Integration Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_930(bad)
    try: build_930("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.30 External Integration Planner")

if __name__=="__main__": main()
