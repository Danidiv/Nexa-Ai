from services.phase8_899_autonomous_production_session import build_899,valid_899
def main():
    o=build_899("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_899(o) and o.valid() and o.setup=="8.99" and o.kind=="Autonomous Production Session"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_899(bad)
    try: build_899("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.99 Autonomous Production Session")
if __name__=="__main__": main()
