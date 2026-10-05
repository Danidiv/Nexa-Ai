from services.phase8_894_scaling_decision_engine import build_894,valid_894
def main():
    o=build_894("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_894(o) and o.valid() and o.setup=="8.94" and o.kind=="Scaling Decision Engine"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_894(bad)
    try: build_894("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.94 Scaling Decision Engine")
if __name__=="__main__": main()
