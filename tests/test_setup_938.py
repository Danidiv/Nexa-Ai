from services.phase9_938_saas_security_hardening_planner import build_938,valid_938

def main():
    o=build_938("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.38","goal":"saas"},risk="low")
    assert valid_938(o) and o.valid() and o.setup=="9.38" and o.kind=="SaaS Security Hardening Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_938(bad)
    try: build_938("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.38 SaaS Security Hardening Planner")

if __name__=="__main__": main()
