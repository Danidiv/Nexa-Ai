from services.phase8_844_browser_driven_implementation import build_844, valid_844

def main():
    obj=build_844("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_844(obj)
    assert obj.setup=="8.44"
    assert obj.kind=="Browser-Driven Implementation Controller"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_844(bad)
    try: build_844("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.44 Browser-Driven Implementation Controller")

if __name__=="__main__": main()
