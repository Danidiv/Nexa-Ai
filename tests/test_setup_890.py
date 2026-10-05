from services.phase8_890_tenant_isolation_guard import build_890,valid_890
def main():
    o=build_890("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_890(o) and o.valid() and o.setup=="8.90" and o.kind=="Tenant Isolation Guard"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_890(bad)
    try: build_890("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.90 Tenant Isolation Guard")
if __name__=="__main__": main()
