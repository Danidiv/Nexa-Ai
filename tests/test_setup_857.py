from services.phase8_857_command_permission_planner import build_857,valid_857
def main():
    o=build_857("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_857(o) and o.valid() and o.setup=="8.57" and o.kind=="Command Permission Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_857(bad)
    try: build_857("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.57 Command Permission Planner")
if __name__=="__main__": main()
