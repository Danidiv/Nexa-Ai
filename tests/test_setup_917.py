from services.phase9_917_api_response_contract_guard import build_917,valid_917

def main():
    o=build_917("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.17","goal":"saas"},risk="low")
    assert valid_917(o) and o.valid() and o.setup=="9.17" and o.kind=="API Response Contract Guard"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_917(bad)
    try: build_917("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.17 API Response Contract Guard")

if __name__=="__main__": main()
