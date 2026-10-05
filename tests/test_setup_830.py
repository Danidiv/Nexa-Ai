from services.phase8_830_end_to_end_execution_controller import build_830, valid_830

def main():
    obj=build_830("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_830(obj)
    assert obj.setup=="8.30"
    assert obj.kind=="End-to-End Execution Controller"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_830(bad)
    try: build_830("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.30 End-to-End Execution Controller")

if __name__=="__main__": main()
