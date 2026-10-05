from services.phase10_package_dependency_executor import build_962, valid_962

def main():
    o=build_962("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"962"}, risk="low")
    assert valid_962(o) and o.valid() and o.setup=="962" and o.kind=="Package Dependency Executor"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_962(bad)
    try: build_962("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 962 Package Dependency Executor")

if __name__=="__main__": main()
