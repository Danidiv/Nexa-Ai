from services.phase7_766_database_migration_plan import build_766, valid_766

def main():
    obj=build_766("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_766(obj)
    assert obj.setup == "7.66"
    assert obj.kind == "Database Migration Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_766(tampered)
    try:
        build_766("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.66 Database Migration Plan")

if __name__ == "__main__": main()
