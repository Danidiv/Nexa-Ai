from services.phase9_922_ui_component_contract import build_922,valid_922

def main():
    o=build_922("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.22","goal":"saas"},risk="low")
    assert valid_922(o) and o.valid() and o.setup=="9.22" and o.kind=="UI Component Contract"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_922(bad)
    try: build_922("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.22 UI Component Contract")

if __name__=="__main__": main()
