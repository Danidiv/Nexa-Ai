from services.phase8_838_security_qa_coordinator import build_838, valid_838

def main():
    obj=build_838("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_838(obj)
    assert obj.setup=="8.38"
    assert obj.kind=="Security QA Coordinator"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_838(bad)
    try: build_838("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.38 Security QA Coordinator")

if __name__=="__main__": main()
