from services.phase8_805_feature_dependency_mapping import build_805, valid_805

def main():
    obj=build_805("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_805(obj)
    assert obj.setup=="8.05"
    assert obj.kind=="Feature Dependency Mapping"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_805(bad)
    try: build_805("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.05 Feature Dependency Mapping")

if __name__=="__main__": main()
