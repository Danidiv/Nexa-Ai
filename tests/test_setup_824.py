from services.phase8_824_api_execution_coordinator import build_824, valid_824

def main():
    obj=build_824("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_824(obj)
    assert obj.setup=="8.24"
    assert obj.kind=="API Execution Coordinator"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_824(bad)
    try: build_824("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.24 API Execution Coordinator")

if __name__=="__main__": main()
