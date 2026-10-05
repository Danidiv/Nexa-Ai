from services.phase8_862_configuration_drift_guard import build_862,valid_862
def main():
    o=build_862("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_862(o) and o.valid() and o.setup=="8.62" and o.kind=="Configuration Drift Guard"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_862(bad)
    try: build_862("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.62 Configuration Drift Guard")
if __name__=="__main__": main()
