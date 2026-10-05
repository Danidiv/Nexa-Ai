from services.phase8_892_cost_efficiency_analyzer import build_892,valid_892
def main():
    o=build_892("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_892(o) and o.valid() and o.setup=="8.92" and o.kind=="Cost Efficiency Analyzer"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_892(bad)
    try: build_892("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.92 Cost Efficiency Analyzer")
if __name__=="__main__": main()
