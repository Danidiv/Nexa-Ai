from services.phase8_845_autonomous_debug_session import build_845, valid_845

def main():
    obj=build_845("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_845(obj)
    assert obj.setup=="8.45"
    assert obj.kind=="Autonomous Debug Session"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_845(bad)
    try: build_845("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.45 Autonomous Debug Session")

if __name__=="__main__": main()
