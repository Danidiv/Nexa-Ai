from services.phase10_health_slo_monitor import build_973, valid_973

def main():
    o=build_973("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"973"}, risk="low")
    assert valid_973(o) and o.valid() and o.setup=="973" and o.kind=="Health SLO Monitor"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_973(bad)
    try: build_973("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 973 Health SLO Monitor")

if __name__=="__main__": main()
