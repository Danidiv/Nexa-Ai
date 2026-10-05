from services.phase9_904_authorization_policy_compiler import build_904,valid_904

def main():
    o=build_904("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.04","goal":"saas"},risk="low")
    assert valid_904(o) and o.valid() and o.setup=="9.04" and o.kind=="Authorization Policy Compiler"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_904(bad)
    try: build_904("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.04 Authorization Policy Compiler")

if __name__=="__main__": main()
