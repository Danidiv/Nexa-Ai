from services.phase10_autonomous_repair_loop import build_970, valid_970

def main():
    o=build_970("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"970"}, risk="low")
    assert valid_970(o) and o.valid() and o.setup=="970" and o.kind=="Autonomous Repair Loop"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_970(bad)
    try: build_970("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 970 Autonomous Repair Loop")

if __name__=="__main__": main()
