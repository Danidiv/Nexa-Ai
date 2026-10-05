from services.phase8_887_feature_rollout_coordinator import build_887,valid_887
def main():
    o=build_887("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_887(o) and o.valid() and o.setup=="8.87" and o.kind=="Feature Rollout Coordinator"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_887(bad)
    try: build_887("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.87 Feature Rollout Coordinator")
if __name__=="__main__": main()
