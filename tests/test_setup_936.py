from services.phase9_936_data_retention_planner import build_936,valid_936

def main():
    o=build_936("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.36","goal":"saas"},risk="low")
    assert valid_936(o) and o.valid() and o.setup=="9.36" and o.kind=="Data Retention Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_936(bad)
    try: build_936("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.36 Data Retention Planner")

if __name__=="__main__": main()
