from services.phase9_934_observability_dashboard_planner import build_934,valid_934

def main():
    o=build_934("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.34","goal":"saas"},risk="low")
    assert valid_934(o) and o.valid() and o.setup=="9.34" and o.kind=="Observability Dashboard Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_934(bad)
    try: build_934("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.34 Observability Dashboard Planner")

if __name__=="__main__": main()
