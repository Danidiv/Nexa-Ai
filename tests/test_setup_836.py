from services.phase8_836_accessibility_qa_coordinator import build_836, valid_836

def main():
    obj=build_836("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_836(obj)
    assert obj.setup=="8.36"
    assert obj.kind=="Accessibility QA Coordinator"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_836(bad)
    try: build_836("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.36 Accessibility QA Coordinator")

if __name__=="__main__": main()
