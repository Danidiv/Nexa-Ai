from services.phase9_947_autonomous_product_repair_planner import build_947,valid_947

def main():
    o=build_947("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.47","goal":"saas"},risk="low")
    assert valid_947(o) and o.valid() and o.setup=="9.47" and o.kind=="Autonomous Product Repair Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_947(bad)
    try: build_947("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.47 Autonomous Product Repair Planner")

if __name__=="__main__": main()
