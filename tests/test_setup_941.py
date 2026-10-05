from services.phase9_941_release_change_set_planner import build_941,valid_941

def main():
    o=build_941("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.41","goal":"saas"},risk="low")
    assert valid_941(o) and o.valid() and o.setup=="9.41" and o.kind=="Release Change Set Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_941(bad)
    try: build_941("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.41 Release Change Set Planner")

if __name__=="__main__": main()
