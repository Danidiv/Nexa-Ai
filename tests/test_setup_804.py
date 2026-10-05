from services.phase8_804_acceptance_criteria_generation import build_804, valid_804

def main():
    obj=build_804("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_804(obj)
    assert obj.setup=="8.04"
    assert obj.kind=="Acceptance Criteria Generation"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_804(bad)
    try: build_804("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.04 Acceptance Criteria Generation")

if __name__=="__main__": main()
