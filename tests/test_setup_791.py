from services.phase7_791_requirement_to_implementation_trace import build_791, valid_791

def main():
    obj=build_791("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_791(obj)
    assert obj.setup == "7.91"
    assert obj.kind == "Requirement-to-Implementation Trace"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_791(tampered)
    try:
        build_791("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.91 Requirement-to-Implementation Trace")

if __name__ == "__main__": main()
