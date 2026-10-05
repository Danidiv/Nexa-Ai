from services.phase8_816_database_migration_specification import build_816, valid_816

def main():
    obj=build_816("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_816(obj)
    assert obj.setup=="8.16"
    assert obj.kind=="Database Migration Specification"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_816(bad)
    try: build_816("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.16 Database Migration Specification")

if __name__=="__main__": main()
