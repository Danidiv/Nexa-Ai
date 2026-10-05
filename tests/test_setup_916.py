from services.phase9_916_api_request_validation_planner import build_916,valid_916

def main():
    o=build_916("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.16","goal":"saas"},risk="low")
    assert valid_916(o) and o.valid() and o.setup=="9.16" and o.kind=="API Request Validation Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_916(bad)
    try: build_916("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.16 API Request Validation Planner")

if __name__=="__main__": main()
