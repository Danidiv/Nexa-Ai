from services.phase8_867_frontend_runtime_contract import build_867,valid_867
def main():
    o=build_867("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_867(o) and o.valid() and o.setup=="8.67" and o.kind=="Frontend Runtime Contract"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_867(bad)
    try: build_867("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.67 Frontend Runtime Contract")
if __name__=="__main__": main()
