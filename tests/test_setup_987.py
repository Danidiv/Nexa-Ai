from services.phase10_dependency_upgrade_engine import build_987, valid_987

def main():
    o=build_987("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"987"}, risk="low")
    assert valid_987(o) and o.valid() and o.setup=="987" and o.kind=="Dependency Upgrade Engine"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_987(bad)
    try: build_987("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 987 Dependency Upgrade Engine")

if __name__=="__main__": main()
