from services.phase10_performance_optimization_engine import build_985, valid_985

def main():
    o=build_985("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"985"}, risk="low")
    assert valid_985(o) and o.valid() and o.setup=="985" and o.kind=="Performance Optimization Engine"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_985(bad)
    try: build_985("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 985 Performance Optimization Engine")

if __name__=="__main__": main()
