from services.phase7_767_dependency_change_plan import build_767, valid_767

def main():
    obj=build_767("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_767(obj)
    assert obj.setup == "7.67"
    assert obj.kind == "Dependency Change Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_767(tampered)
    try:
        build_767("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.67 Dependency Change Plan")

if __name__ == "__main__": main()
