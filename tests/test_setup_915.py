from services.phase9_915_api_route_compiler import build_915,valid_915

def main():
    o=build_915("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.15","goal":"saas"},risk="low")
    assert valid_915(o) and o.valid() and o.setup=="9.15" and o.kind=="API Route Compiler"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_915(bad)
    try: build_915("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.15 API Route Compiler")

if __name__=="__main__": main()
