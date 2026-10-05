from services.phase7_783_database_qa_plan import build_783, valid_783

def main():
    obj=build_783("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_783(obj)
    assert obj.setup == "7.83"
    assert obj.kind == "Database QA Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_783(tampered)
    try:
        build_783("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.83 Database QA Plan")

if __name__ == "__main__": main()
