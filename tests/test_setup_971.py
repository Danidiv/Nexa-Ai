from services.phase10_deployment_executor import build_971, valid_971

def main():
    o=build_971("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"971"}, risk="low")
    assert valid_971(o) and o.valid() and o.setup=="971" and o.kind=="Deployment Executor"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_971(bad)
    try: build_971("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 971 Deployment Executor")

if __name__=="__main__": main()
