from services.phase9_928_background_job_planner import build_928,valid_928

def main():
    o=build_928("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.28","goal":"saas"},risk="low")
    assert valid_928(o) and o.valid() and o.setup=="9.28" and o.kind=="Background Job Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_928(bad)
    try: build_928("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.28 Background Job Planner")

if __name__=="__main__": main()
