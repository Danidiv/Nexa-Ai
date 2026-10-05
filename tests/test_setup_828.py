from services.phase8_828_failure_diagnosis_engine import build_828, valid_828

def main():
    obj=build_828("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_828(obj)
    assert obj.setup=="8.28"
    assert obj.kind=="Failure Diagnosis Engine"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_828(bad)
    try: build_828("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.28 Failure Diagnosis Engine")

if __name__=="__main__": main()
