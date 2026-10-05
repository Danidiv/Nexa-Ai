from services.phase8_827_user_flow_execution_coordinator import build_827, valid_827

def main():
    obj=build_827("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_827(obj)
    assert obj.setup=="8.27"
    assert obj.kind=="User Flow Execution Coordinator"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_827(bad)
    try: build_827("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.27 User Flow Execution Coordinator")

if __name__=="__main__": main()
