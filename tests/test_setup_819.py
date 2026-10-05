from services.phase8_819_full_stack_change_graph import build_819, valid_819

def main():
    obj=build_819("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_819(obj)
    assert obj.setup=="8.19"
    assert obj.kind=="Full-Stack Change Graph"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_819(bad)
    try: build_819("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.19 Full-Stack Change Graph")

if __name__=="__main__": main()
