from services.phase7_769_full_stack_change_plan import build_769, valid_769

def main():
    obj=build_769("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_769(obj)
    assert obj.setup == "7.69"
    assert obj.kind == "Full-Stack Change Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_769(tampered)
    try:
        build_769("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.69 Full-Stack Change Plan")

if __name__ == "__main__": main()
