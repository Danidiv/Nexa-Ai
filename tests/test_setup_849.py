from services.phase8_849_autonomous_product_session import build_849, valid_849

def main():
    obj=build_849("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_849(obj)
    assert obj.setup=="8.49"
    assert obj.kind=="Autonomous Product Session"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_849(bad)
    try: build_849("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.49 Autonomous Product Session")

if __name__=="__main__": main()
