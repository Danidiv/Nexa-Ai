from services.phase8_833_database_qa_coordinator import build_833, valid_833

def main():
    obj=build_833("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_833(obj)
    assert obj.setup=="8.33"
    assert obj.kind=="Database QA Coordinator"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_833(bad)
    try: build_833("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.33 Database QA Coordinator")

if __name__=="__main__": main()
