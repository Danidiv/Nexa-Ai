from services.phase7_795_autonomous_debug_session import build_795, valid_795

def main():
    obj=build_795("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_795(obj)
    assert obj.setup == "7.95"
    assert obj.kind == "Autonomous Debug Session"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_795(tampered)
    try:
        build_795("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.95 Autonomous Debug Session")

if __name__ == "__main__": main()
