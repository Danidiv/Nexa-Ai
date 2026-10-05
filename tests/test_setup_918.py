from services.phase9_918_api_error_contract import build_918,valid_918

def main():
    o=build_918("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.18","goal":"saas"},risk="low")
    assert valid_918(o) and o.valid() and o.setup=="9.18" and o.kind=="API Error Contract"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_918(bad)
    try: build_918("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.18 API Error Contract")

if __name__=="__main__": main()
