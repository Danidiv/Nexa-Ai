from services.phase7_778_failure_diagnosis_record import build_778, valid_778

def main():
    obj=build_778("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_778(obj)
    assert obj.setup == "7.78"
    assert obj.kind == "Failure Diagnosis Record"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_778(tampered)
    try:
        build_778("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.78 Failure Diagnosis Record")

if __name__ == "__main__": main()
