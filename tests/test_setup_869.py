from services.phase8_869_browser_compatibility_gate import build_869,valid_869
def main():
    o=build_869("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_869(o) and o.valid() and o.setup=="8.69" and o.kind=="Browser Compatibility Gate"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_869(bad)
    try: build_869("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.69 Browser Compatibility Gate")
if __name__=="__main__": main()
