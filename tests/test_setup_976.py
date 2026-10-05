from services.phase10_canary_rollback_controller import build_976, valid_976

def main():
    o=build_976("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"976"}, risk="low")
    assert valid_976(o) and o.valid() and o.setup=="976" and o.kind=="Canary Rollback Controller"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_976(bad)
    try: build_976("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 976 Canary Rollback Controller")

if __name__=="__main__": main()
