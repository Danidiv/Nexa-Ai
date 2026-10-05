from services.phase7_757_backend_architecture_plan import build_757, valid_757

def main():
    obj=build_757("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_757(obj)
    assert obj.setup == "7.57"
    assert obj.kind == "Backend Architecture Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_757(tampered)
    try:
        build_757("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.57 Backend Architecture Plan")

if __name__ == "__main__": main()
