from services.phase10_ux_improvement_engine import build_984, valid_984

def main():
    o=build_984("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"984"}, risk="low")
    assert valid_984(o) and o.valid() and o.setup=="984" and o.kind=="UX Improvement Engine"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_984(bad)
    try: build_984("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 984 UX Improvement Engine")

if __name__=="__main__": main()
