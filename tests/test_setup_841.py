from services.phase8_841_requirement_trace import build_841, valid_841

def main():
    obj=build_841("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_841(obj)
    assert obj.setup=="8.41"
    assert obj.kind=="Requirement-to-Implementation Trace"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_841(bad)
    try: build_841("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.41 Requirement-to-Implementation Trace")

if __name__=="__main__": main()
