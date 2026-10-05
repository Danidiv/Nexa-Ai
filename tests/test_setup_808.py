from services.phase8_808_frontend_architecture_synthesis import build_808, valid_808

def main():
    obj=build_808("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_808(obj)
    assert obj.setup=="8.08"
    assert obj.kind=="Frontend Architecture Synthesis"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_808(bad)
    try: build_808("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.08 Frontend Architecture Synthesis")

if __name__=="__main__": main()
