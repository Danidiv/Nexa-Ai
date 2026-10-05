from services.phase8_820_implementation_task_compiler import build_820, valid_820

def main():
    obj=build_820("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_820(obj)
    assert obj.setup=="8.20"
    assert obj.kind=="Implementation Task Compiler"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_820(bad)
    try: build_820("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.20 Implementation Task Compiler")

if __name__=="__main__": main()
