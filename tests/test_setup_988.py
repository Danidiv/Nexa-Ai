from services.phase10_cost_optimization_engine import build_988, valid_988

def main():
    o=build_988("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"988"}, risk="low")
    assert valid_988(o) and o.valid() and o.setup=="988" and o.kind=="Cost Optimization Engine"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_988(bad)
    try: build_988("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 988 Cost Optimization Engine")

if __name__=="__main__": main()
