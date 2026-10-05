from services.phase10_environment_bootstrap_executor import build_963, valid_963

def main():
    o=build_963("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"963"}, risk="low")
    assert valid_963(o) and o.valid() and o.setup=="963" and o.kind=="Environment Bootstrap Executor"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_963(bad)
    try: build_963("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 963 Environment Bootstrap Executor")

if __name__=="__main__": main()
