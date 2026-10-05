from services.phase9_919_api_rate_limit_planner import build_919,valid_919

def main():
    o=build_919("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.19","goal":"saas"},risk="low")
    assert valid_919(o) and o.valid() and o.setup=="9.19" and o.kind=="API Rate Limit Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_919(bad)
    try: build_919("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.19 API Rate Limit Planner")

if __name__=="__main__": main()
