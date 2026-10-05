from services.phase9_901_tenant_architecture_model import build_901,valid_901

def main():
    o=build_901("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.01","goal":"saas"},risk="low")
    assert valid_901(o) and o.valid() and o.setup=="9.01" and o.kind=="Tenant Architecture Model"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_901(bad)
    try: build_901("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.01 Tenant Architecture Model")

if __name__=="__main__": main()
