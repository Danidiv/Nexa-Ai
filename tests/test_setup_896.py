from services.phase8_896_disaster_recovery_coordinator import build_896,valid_896
def main():
    o=build_896("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_896(o) and o.valid() and o.setup=="8.96" and o.kind=="Disaster Recovery Coordinator"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_896(bad)
    try: build_896("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.96 Disaster Recovery Coordinator")
if __name__=="__main__": main()
