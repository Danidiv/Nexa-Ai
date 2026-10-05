from services.phase9_939_operational_runbook_compiler import build_939,valid_939

def main():
    o=build_939("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.39","goal":"saas"},risk="low")
    assert valid_939(o) and o.valid() and o.setup=="9.39" and o.kind=="Operational Runbook Compiler"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_939(bad)
    try: build_939("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.39 Operational Runbook Compiler")

if __name__=="__main__": main()
