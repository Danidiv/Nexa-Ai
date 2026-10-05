from services.phase8_848_completion_evidence_bundle import build_848, valid_848

def main():
    obj=build_848("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_848(obj)
    assert obj.setup=="8.48"
    assert obj.kind=="Completion Evidence Bundle"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_848(bad)
    try: build_848("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.48 Completion Evidence Bundle")

if __name__=="__main__": main()
