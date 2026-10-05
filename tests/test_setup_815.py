from services.phase8_815_api_generation_specification import build_815, valid_815

def main():
    obj=build_815("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_815(obj)
    assert obj.setup=="8.15"
    assert obj.kind=="API Generation Specification"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_815(bad)
    try: build_815("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.15 API Generation Specification")

if __name__=="__main__": main()
