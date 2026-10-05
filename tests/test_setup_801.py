from services.phase8_801_spec_normalization import build_801, valid_801

def main():
    obj=build_801("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_801(obj)
    assert obj.setup=="8.01"
    assert obj.kind=="Product Specification Normalization"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_801(bad)
    try: build_801("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.01 Product Specification Normalization")

if __name__=="__main__": main()
