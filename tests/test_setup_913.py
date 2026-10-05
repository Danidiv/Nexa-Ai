from services.phase9_913_seed_data_planner import build_913,valid_913

def main():
    o=build_913("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.13","goal":"saas"},risk="low")
    assert valid_913(o) and o.valid() and o.setup=="9.13" and o.kind=="Seed Data Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_913(bad)
    try: build_913("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.13 Seed Data Planner")

if __name__=="__main__": main()
