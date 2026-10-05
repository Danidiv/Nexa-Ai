from services.phase10_api_implementation_executor import build_965, valid_965

def main():
    o=build_965("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"965"}, risk="low")
    assert valid_965(o) and o.valid() and o.setup=="965" and o.kind=="API Implementation Executor"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_965(bad)
    try: build_965("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 965 API Implementation Executor")

if __name__=="__main__": main()
