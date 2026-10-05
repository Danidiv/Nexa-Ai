from services.phase8_885_product_improvement_planner import build_885,valid_885
def main():
    o=build_885("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_885(o) and o.valid() and o.setup=="8.85" and o.kind=="Product Improvement Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_885(bad)
    try: build_885("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.85 Product Improvement Planner")
if __name__=="__main__": main()
