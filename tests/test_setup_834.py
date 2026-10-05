from services.phase8_834_ui_qa_coordinator import build_834, valid_834

def main():
    obj=build_834("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_834(obj)
    assert obj.setup=="8.34"
    assert obj.kind=="UI QA Coordinator"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_834(bad)
    try: build_834("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.34 UI QA Coordinator")

if __name__=="__main__": main()
