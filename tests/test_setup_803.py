from services.phase8_803_user_story_generation import build_803, valid_803

def main():
    obj=build_803("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_803(obj)
    assert obj.setup=="8.03"
    assert obj.kind=="User Story Generation"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_803(bad)
    try: build_803("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.03 User Story Generation")

if __name__=="__main__": main()
