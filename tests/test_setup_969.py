from services.phase10_failure_triage_engine import build_969, valid_969

def main():
    o=build_969("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"969"}, risk="low")
    assert valid_969(o) and o.valid() and o.setup=="969" and o.kind=="Failure Triage Engine"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_969(bad)
    try: build_969("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 969 Failure Triage Engine")

if __name__=="__main__": main()
