from services.phase9_925_dashboard_composition_planner import build_925,valid_925

def main():
    o=build_925("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.25","goal":"saas"},risk="low")
    assert valid_925(o) and o.valid() and o.setup=="9.25" and o.kind=="Dashboard Composition Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_925(bad)
    try: build_925("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.25 Dashboard Composition Planner")

if __name__=="__main__": main()
