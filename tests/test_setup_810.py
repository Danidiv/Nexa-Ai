from services.phase8_810_database_architecture_synthesis import build_810, valid_810

def main():
    obj=build_810("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_810(obj)
    assert obj.setup=="8.10"
    assert obj.kind=="Database Architecture Synthesis"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_810(bad)
    try: build_810("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.10 Database Architecture Synthesis")

if __name__=="__main__": main()
