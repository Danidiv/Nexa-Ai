from services.phase7_773_runtime_health_snapshot import build_773, valid_773

def main():
    obj=build_773("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_773(obj)
    assert obj.setup == "7.73"
    assert obj.kind == "Runtime Health Snapshot"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_773(tampered)
    try:
        build_773("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.73 Runtime Health Snapshot")

if __name__ == "__main__": main()
