from services.phase8_825_database_execution_coordinator import build_825, valid_825

def main():
    obj=build_825("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_825(obj)
    assert obj.setup=="8.25"
    assert obj.kind=="Database Execution Coordinator"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_825(bad)
    try: build_825("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.25 Database Execution Coordinator")

if __name__=="__main__": main()
