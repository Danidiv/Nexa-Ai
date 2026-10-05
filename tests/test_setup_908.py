from services.phase9_908_usage_entitlement_guard import build_908,valid_908

def main():
    o=build_908("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.08","goal":"saas"},risk="low")
    assert valid_908(o) and o.valid() and o.setup=="9.08" and o.kind=="Usage Entitlement Guard"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_908(bad)
    try: build_908("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.08 Usage Entitlement Guard")

if __name__=="__main__": main()
