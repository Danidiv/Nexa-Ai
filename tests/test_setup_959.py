from services.phase10_tenant_safe_audit_search import build_959, valid_959

def main():
    o=build_959("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"959"}, risk="low")
    assert valid_959(o) and o.valid() and o.setup=="959" and o.kind=="Tenant Safe Audit Search"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_959(bad)
    try: build_959("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 959 Tenant Safe Audit Search")

if __name__=="__main__": main()
