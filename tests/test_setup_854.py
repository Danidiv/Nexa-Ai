from services.phase8_854_change_risk_analyzer import build_854,valid_854
def main():
    o=build_854("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_854(o) and o.valid() and o.setup=="8.54" and o.kind=="Change Risk Analyzer"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_854(bad)
    try: build_854("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.54 Change Risk Analyzer")
if __name__=="__main__": main()
