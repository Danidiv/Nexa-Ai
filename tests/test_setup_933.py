from services.phase9_933_audit_trail_planner import build_933,valid_933

def main():
    o=build_933("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.33","goal":"saas"},risk="low")
    assert valid_933(o) and o.valid() and o.setup=="9.33" and o.kind=="Audit Trail Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_933(bad)
    try: build_933("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.33 Audit Trail Planner")

if __name__=="__main__": main()
