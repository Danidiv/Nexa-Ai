from services.phase8_812_ui_component_planning import build_812, valid_812

def main():
    obj=build_812("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_812(obj)
    assert obj.setup=="8.12"
    assert obj.kind=="UI Component Planning"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_812(bad)
    try: build_812("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.12 UI Component Planning")

if __name__=="__main__": main()
