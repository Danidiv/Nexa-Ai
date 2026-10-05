from services.phase8_886_experiment_planning_contract import build_886,valid_886
def main():
    o=build_886("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_886(o) and o.valid() and o.setup=="8.86" and o.kind=="Experiment Planning Contract"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_886(bad)
    try: build_886("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.86 Experiment Planning Contract")
if __name__=="__main__": main()
