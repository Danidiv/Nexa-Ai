from services.phase9_935_product_analytics_event_planner import build_935,valid_935

def main():
    o=build_935("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.35","goal":"saas"},risk="low")
    assert valid_935(o) and o.valid() and o.setup=="9.35" and o.kind=="Product Analytics Event Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_935(bad)
    try: build_935("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.35 Product Analytics Event Planner")

if __name__=="__main__": main()
