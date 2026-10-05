from services.phase9_906_saas_workspace_model import build_906,valid_906

def main():
    o=build_906("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.06","goal":"saas"},risk="low")
    assert valid_906(o) and o.valid() and o.setup=="9.06" and o.kind=="SaaS Workspace Model"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_906(bad)
    try: build_906("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.06 SaaS Workspace Model")

if __name__=="__main__": main()
