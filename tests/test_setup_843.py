from services.phase8_843_full_stack_generation_session import build_843, valid_843

def main():
    obj=build_843("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_843(obj)
    assert obj.setup=="8.43"
    assert obj.kind=="Full-Stack Generation Session"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_843(bad)
    try: build_843("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.43 Full-Stack Generation Session")

if __name__=="__main__": main()
