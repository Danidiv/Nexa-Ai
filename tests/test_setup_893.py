from services.phase8_893_capacity_planning_contract import build_893,valid_893
def main():
    o=build_893("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_893(o) and o.valid() and o.setup=="8.93" and o.kind=="Capacity Planning Contract"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_893(bad)
    try: build_893("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.93 Capacity Planning Contract")
if __name__=="__main__": main()
