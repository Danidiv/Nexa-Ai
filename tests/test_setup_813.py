from services.phase8_813_page_generation_specification import build_813, valid_813

def main():
    obj=build_813("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_813(obj)
    assert obj.setup=="8.13"
    assert obj.kind=="Page Generation Specification"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_813(bad)
    try: build_813("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.13 Page Generation Specification")

if __name__=="__main__": main()
