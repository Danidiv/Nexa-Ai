from services.phase10_ui_implementation_executor import build_966, valid_966

def main():
    o=build_966("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"966"}, risk="low")
    assert valid_966(o) and o.valid() and o.setup=="966" and o.kind=="UI Implementation Executor"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_966(bad)
    try: build_966("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 966 UI Implementation Executor")

if __name__=="__main__": main()
