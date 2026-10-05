from services.phase9_940_environment_promotion_planner import build_940,valid_940

def main():
    o=build_940("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.40","goal":"saas"},risk="low")
    assert valid_940(o) and o.valid() and o.setup=="9.40" and o.kind=="Environment Promotion Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_940(bad)
    try: build_940("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.40 Environment Promotion Planner")

if __name__=="__main__": main()
