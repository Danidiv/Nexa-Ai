from services.phase7_764_backend_service_plan import build_764, valid_764

def main():
    obj=build_764("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_764(obj)
    assert obj.setup == "7.64"
    assert obj.kind == "Backend Service Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_764(tampered)
    try:
        build_764("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.64 Backend Service Plan")

if __name__ == "__main__": main()
