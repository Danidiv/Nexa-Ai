from services.phase8_821_build_execution_coordinator import build_821, valid_821

def main():
    obj=build_821("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_821(obj)
    assert obj.setup=="8.21"
    assert obj.kind=="Build Execution Coordinator"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_821(bad)
    try: build_821("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.21 Build Execution Coordinator")

if __name__=="__main__": main()
