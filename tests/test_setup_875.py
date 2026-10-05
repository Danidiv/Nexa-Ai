from services.phase8_875_observability_contract import build_875,valid_875
def main():
    o=build_875("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_875(o) and o.valid() and o.setup=="8.75" and o.kind=="Observability Contract"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_875(bad)
    try: build_875("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.75 Observability Contract")
if __name__=="__main__": main()
