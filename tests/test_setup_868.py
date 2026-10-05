from services.phase8_868_backend_runtime_contract import build_868,valid_868
def main():
    o=build_868("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_868(o) and o.valid() and o.setup=="8.68" and o.kind=="Backend Runtime Contract"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_868(bad)
    try: build_868("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.68 Backend Runtime Contract")
if __name__=="__main__": main()
