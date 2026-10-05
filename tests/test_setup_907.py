from services.phase9_907_billing_model import build_907,valid_907

def main():
    o=build_907("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.07","goal":"saas"},risk="low")
    assert valid_907(o) and o.valid() and o.setup=="9.07" and o.kind=="Billing Model"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_907(bad)
    try: build_907("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.07 Billing Model")

if __name__=="__main__": main()
