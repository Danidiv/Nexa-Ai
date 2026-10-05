from services.phase8_831_functional_qa_coordinator import build_831, valid_831

def main():
    obj=build_831("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_831(obj)
    assert obj.setup=="8.31"
    assert obj.kind=="Functional QA Coordinator"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_831(bad)
    try: build_831("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.31 Functional QA Coordinator")

if __name__=="__main__": main()
