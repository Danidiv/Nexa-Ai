from services.phase10_browser_implementation_loop import build_967, valid_967

def main():
    o=build_967("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"967"}, risk="low")
    assert valid_967(o) and o.valid() and o.setup=="967" and o.kind=="Browser Implementation Loop"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_967(bad)
    try: build_967("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 967 Browser Implementation Loop")

if __name__=="__main__": main()
