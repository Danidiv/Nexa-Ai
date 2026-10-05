from services.phase9_923_form_workflow_planner import build_923,valid_923

def main():
    o=build_923("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.23","goal":"saas"},risk="low")
    assert valid_923(o) and o.valid() and o.setup=="9.23" and o.kind=="Form Workflow Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_923(bad)
    try: build_923("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.23 Form Workflow Planner")

if __name__=="__main__": main()
