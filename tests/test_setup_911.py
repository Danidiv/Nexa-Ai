from services.phase9_911_relational_schema_planner import build_911,valid_911

def main():
    o=build_911("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.11","goal":"saas"},risk="low")
    assert valid_911(o) and o.valid() and o.setup=="9.11" and o.kind=="Relational Schema Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_911(bad)
    try: build_911("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.11 Relational Schema Planner")

if __name__=="__main__": main()
