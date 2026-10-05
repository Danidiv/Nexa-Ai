from services.phase10_capacity_planning_engine import build_989, valid_989

def main():
    o=build_989("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"989"}, risk="low")
    assert valid_989(o) and o.valid() and o.setup=="989" and o.kind=="Capacity Planning Engine"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_989(bad)
    try: build_989("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 989 Capacity Planning Engine")

if __name__=="__main__": main()
