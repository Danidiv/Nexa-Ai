from services.phase7_774_api_execution_record import build_774, valid_774

def main():
    obj=build_774("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_774(obj)
    assert obj.setup == "7.74"
    assert obj.kind == "API Execution Record"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_774(tampered)
    try:
        build_774("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.74 API Execution Record")

if __name__ == "__main__": main()
