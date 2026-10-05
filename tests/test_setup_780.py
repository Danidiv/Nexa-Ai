from services.phase7_780_end_to_end_execution_record import build_780, valid_780

def main():
    obj=build_780("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_780(obj)
    assert obj.setup == "7.80"
    assert obj.kind == "End-to-End Execution Record"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_780(tampered)
    try:
        build_780("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.80 End-to-End Execution Record")

if __name__ == "__main__": main()
