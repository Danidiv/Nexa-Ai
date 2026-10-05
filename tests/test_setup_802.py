from services.phase8_802_requirement_clarification import build_802, valid_802

def main():
    obj=build_802("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_802(obj)
    assert obj.setup=="8.02"
    assert obj.kind=="Requirement Clarification Model"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_802(bad)
    try: build_802("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.02 Requirement Clarification Model")

if __name__=="__main__": main()
