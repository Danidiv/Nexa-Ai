from services.phase8_832_api_qa_coordinator import build_832, valid_832

def main():
    obj=build_832("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_832(obj)
    assert obj.setup=="8.32"
    assert obj.kind=="API QA Coordinator"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_832(bad)
    try: build_832("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.32 API QA Coordinator")

if __name__=="__main__": main()
