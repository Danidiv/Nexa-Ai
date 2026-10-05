from services.phase8_861_environment_parity_analyzer import build_861,valid_861
def main():
    o=build_861("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_861(o) and o.valid() and o.setup=="8.61" and o.kind=="Environment Parity Analyzer"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_861(bad)
    try: build_861("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.61 Environment Parity Analyzer")
if __name__=="__main__": main()
