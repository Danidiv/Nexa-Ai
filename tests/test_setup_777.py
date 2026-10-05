from services.phase7_777_user_flow_execution_plan import build_777, valid_777

def main():
    obj=build_777("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_777(obj)
    assert obj.setup == "7.77"
    assert obj.kind == "User Flow Execution Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_777(tampered)
    try:
        build_777("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.77 User Flow Execution Plan")

if __name__ == "__main__": main()
