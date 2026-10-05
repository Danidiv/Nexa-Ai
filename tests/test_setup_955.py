from services.phase10_usage_metering_engine import build_955, valid_955

def main():
    o=build_955("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"955"}, risk="low")
    assert valid_955(o) and o.valid() and o.setup=="955" and o.kind=="Usage Metering Engine"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_955(bad)
    try: build_955("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 955 Usage Metering Engine")

if __name__=="__main__": main()
