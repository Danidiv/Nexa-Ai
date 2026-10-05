from services.phase9_943_customer_support_context import build_943,valid_943

def main():
    o=build_943("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.43","goal":"saas"},risk="low")
    assert valid_943(o) and o.valid() and o.setup=="9.43" and o.kind=="Customer Support Context"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_943(bad)
    try: build_943("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.43 Customer Support Context")

if __name__=="__main__": main()
