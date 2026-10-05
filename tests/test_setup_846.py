from services.phase8_846_regression_repair_controller import build_846, valid_846

def main():
    obj=build_846("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_846(obj)
    assert obj.setup=="8.46"
    assert obj.kind=="Regression Repair Controller"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_846(bad)
    try: build_846("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.46 Regression Repair Controller")

if __name__=="__main__": main()
