from services.phase9_902_identity_model import build_902,valid_902

def main():
    o=build_902("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.02","goal":"saas"},risk="low")
    assert valid_902(o) and o.valid() and o.setup=="9.02" and o.kind=="Identity Model"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_902(bad)
    try: build_902("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.02 Identity Model")

if __name__=="__main__": main()
