from services.phase8_817_dependency_change_resolution import build_817, valid_817

def main():
    obj=build_817("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_817(obj)
    assert obj.setup=="8.17"
    assert obj.kind=="Dependency Change Resolution"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_817(bad)
    try: build_817("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.17 Dependency Change Resolution")

if __name__=="__main__": main()
