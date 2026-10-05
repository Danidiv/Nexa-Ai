from services.phase8_823_runtime_health_analyzer import build_823, valid_823

def main():
    obj=build_823("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_823(obj)
    assert obj.setup=="8.23"
    assert obj.kind=="Runtime Health Analyzer"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_823(bad)
    try: build_823("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.23 Runtime Health Analyzer")

if __name__=="__main__": main()
