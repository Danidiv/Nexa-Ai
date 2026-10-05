from services.phase7_793_full_stack_generation_session import build_793, valid_793

def main():
    obj=build_793("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_793(obj)
    assert obj.setup == "7.93"
    assert obj.kind == "Full-Stack Generation Session"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_793(tampered)
    try:
        build_793("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.93 Full-Stack Generation Session")

if __name__ == "__main__": main()
