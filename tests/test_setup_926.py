from services.phase9_926_client_data_cache_planner import build_926,valid_926

def main():
    o=build_926("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.26","goal":"saas"},risk="low")
    assert valid_926(o) and o.valid() and o.setup=="9.26" and o.kind=="Client Data Cache Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_926(bad)
    try: build_926("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.26 Client Data Cache Planner")

if __name__=="__main__": main()
