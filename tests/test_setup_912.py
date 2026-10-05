from services.phase9_912_migration_execution_planner import build_912,valid_912

def main():
    o=build_912("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.12","goal":"saas"},risk="low")
    assert valid_912(o) and o.valid() and o.setup=="9.12" and o.kind=="Migration Execution Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_912(bad)
    try: build_912("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.12 Migration Execution Planner")

if __name__=="__main__": main()
