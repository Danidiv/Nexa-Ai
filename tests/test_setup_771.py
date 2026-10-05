from services.phase7_771_build_execution_record import build_771, valid_771

def main():
    obj=build_771("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_771(obj)
    assert obj.setup == "7.71"
    assert obj.kind == "Build Execution Record"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_771(tampered)
    try:
        build_771("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.71 Build Execution Record")

if __name__ == "__main__": main()
