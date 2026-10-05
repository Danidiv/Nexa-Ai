from services.phase8_871_deployment_execution_plan import build_871,valid_871
def main():
    o=build_871("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_871(o) and o.valid() and o.setup=="8.71" and o.kind=="Deployment Execution Plan"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_871(bad)
    try: build_871("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.71 Deployment Execution Plan")
if __name__=="__main__": main()
