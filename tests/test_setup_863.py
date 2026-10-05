from services.phase8_863_deployment_preflight_planner import build_863,valid_863
def main():
    o=build_863("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_863(o) and o.valid() and o.setup=="8.63" and o.kind=="Deployment Preflight Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_863(bad)
    try: build_863("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.63 Deployment Preflight Planner")
if __name__=="__main__": main()
