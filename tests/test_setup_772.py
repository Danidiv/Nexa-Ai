from services.phase7_772_development_server_session import build_772, valid_772

def main():
    obj=build_772("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_772(obj)
    assert obj.setup == "7.72"
    assert obj.kind == "Development Server Session"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_772(tampered)
    try:
        build_772("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.72 Development Server Session")

if __name__ == "__main__": main()
