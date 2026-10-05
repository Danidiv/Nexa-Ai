from services.phase9_937_privacy_request_planner import build_937,valid_937

def main():
    o=build_937("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.37","goal":"saas"},risk="low")
    assert valid_937(o) and o.valid() and o.setup=="9.37" and o.kind=="Privacy Request Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_937(bad)
    try: build_937("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.37 Privacy Request Planner")

if __name__=="__main__": main()
