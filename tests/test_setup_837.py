from services.phase8_837_performance_qa_coordinator import build_837, valid_837

def main():
    obj=build_837("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_837(obj)
    assert obj.setup=="8.37"
    assert obj.kind=="Performance QA Coordinator"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_837(bad)
    try: build_837("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.37 Performance QA Coordinator")

if __name__=="__main__": main()
