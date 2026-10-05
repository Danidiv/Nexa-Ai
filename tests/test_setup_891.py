from services.phase8_891_production_security_gate import build_891,valid_891
def main():
    o=build_891("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_891(o) and o.valid() and o.setup=="8.91" and o.kind=="Production Security Gate"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_891(bad)
    try: build_891("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.91 Production Security Gate")
if __name__=="__main__": main()
