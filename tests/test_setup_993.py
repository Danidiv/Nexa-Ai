from services.phase10_long_running_session_controller import build_993, valid_993

def main():
    o=build_993("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"993"}, risk="low")
    assert valid_993(o) and o.valid() and o.setup=="993" and o.kind=="Long Running Session Controller"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_993(bad)
    try: build_993("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 993 Long Running Session Controller")

if __name__=="__main__": main()
