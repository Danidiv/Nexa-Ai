from services.phase8_873_traffic_safety_gate import build_873,valid_873
def main():
    o=build_873("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_873(o) and o.valid() and o.setup=="8.73" and o.kind=="Traffic Safety Gate"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_873(bad)
    try: build_873("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.73 Traffic Safety Gate")
if __name__=="__main__": main()
