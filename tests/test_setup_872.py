from services.phase8_872_canary_release_plan import build_872,valid_872
def main():
    o=build_872("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_872(o) and o.valid() and o.setup=="8.72" and o.kind=="Canary Release Plan"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_872(bad)
    try: build_872("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.72 Canary Release Plan")
if __name__=="__main__": main()
