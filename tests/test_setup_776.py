from services.phase7_776_browser_execution_record import build_776, valid_776

def main():
    obj=build_776("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_776(obj)
    assert obj.setup == "7.76"
    assert obj.kind == "Browser Execution Record"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_776(tampered)
    try:
        build_776("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.76 Browser Execution Record")

if __name__ == "__main__": main()
