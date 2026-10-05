from services.phase9_920_api_idempotency_planner import build_920,valid_920

def main():
    o=build_920("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.20","goal":"saas"},risk="low")
    assert valid_920(o) and o.valid() and o.setup=="9.20" and o.kind=="API Idempotency Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_920(bad)
    try: build_920("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.20 API Idempotency Planner")

if __name__=="__main__": main()
