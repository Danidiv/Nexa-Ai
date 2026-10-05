from services.phase8_884_usage_pattern_analyzer import build_884,valid_884
def main():
    o=build_884("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_884(o) and o.valid() and o.setup=="8.84" and o.kind=="Usage Pattern Analyzer"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_884(bad)
    try: build_884("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.84 Usage Pattern Analyzer")
if __name__=="__main__": main()
