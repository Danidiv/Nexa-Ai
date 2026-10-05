from services.phase9_924_search_filter_planner import build_924,valid_924

def main():
    o=build_924("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.24","goal":"saas"},risk="low")
    assert valid_924(o) and o.valid() and o.setup=="9.24" and o.kind=="Search Filter Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_924(bad)
    try: build_924("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.24 Search Filter Planner")

if __name__=="__main__": main()
