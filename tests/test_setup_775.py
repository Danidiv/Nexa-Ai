from services.phase7_775_database_execution_record import build_775, valid_775

def main():
    obj=build_775("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_775(obj)
    assert obj.setup == "7.75"
    assert obj.kind == "Database Execution Record"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_775(tampered)
    try:
        build_775("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.75 Database Execution Record")

if __name__ == "__main__": main()
