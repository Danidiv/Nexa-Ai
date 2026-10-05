from services.phase8_809_backend_architecture_synthesis import build_809, valid_809

def main():
    obj=build_809("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_809(obj)
    assert obj.setup=="8.09"
    assert obj.kind=="Backend Architecture Synthesis"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_809(bad)
    try: build_809("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.09 Backend Architecture Synthesis")

if __name__=="__main__": main()
