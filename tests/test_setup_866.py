from services.phase8_866_api_compatibility_gate import build_866,valid_866
def main():
    o=build_866("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_866(o) and o.valid() and o.setup=="8.66" and o.kind=="API Compatibility Gate"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_866(bad)
    try: build_866("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.66 API Compatibility Gate")
if __name__=="__main__": main()
