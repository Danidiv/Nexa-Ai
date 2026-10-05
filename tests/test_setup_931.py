from services.phase9_931_webhook_security_planner import build_931,valid_931

def main():
    o=build_931("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.31","goal":"saas"},risk="low")
    assert valid_931(o) and o.valid() and o.setup=="9.31" and o.kind=="Webhook Security Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_931(bad)
    try: build_931("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.31 Webhook Security Planner")

if __name__=="__main__": main()
