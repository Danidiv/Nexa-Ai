from services.phase8_818_environment_configuration import build_818, valid_818

def main():
    obj=build_818("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_818(obj)
    assert obj.setup=="8.18"
    assert obj.kind=="Environment Configuration Planning"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_818(bad)
    try: build_818("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.18 Environment Configuration Planning")

if __name__=="__main__": main()
