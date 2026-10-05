from services.phase8_889_data_privacy_gate import build_889,valid_889
def main():
    o=build_889("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_889(o) and o.valid() and o.setup=="8.89" and o.kind=="Data Privacy Gate"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_889(bad)
    try: build_889("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.89 Data Privacy Gate")
if __name__=="__main__": main()
