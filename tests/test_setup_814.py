from services.phase8_814_backend_service_generation import build_814, valid_814

def main():
    obj=build_814("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_814(obj)
    assert obj.setup=="8.14"
    assert obj.kind=="Backend Service Generation Specification"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_814(bad)
    try: build_814("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.14 Backend Service Generation Specification")

if __name__=="__main__": main()
