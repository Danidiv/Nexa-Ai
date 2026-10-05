from services.phase8_826_browser_execution_coordinator import build_826, valid_826

def main():
    obj=build_826("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_826(obj)
    assert obj.setup=="8.26"
    assert obj.kind=="Browser Execution Coordinator"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_826(bad)
    try: build_826("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.26 Browser Execution Coordinator")

if __name__=="__main__": main()
