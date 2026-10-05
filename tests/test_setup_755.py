from services.phase7_755_architecture_decision_record import build_755, valid_755

def main():
    obj=build_755("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_755(obj)
    assert obj.setup == "7.55"
    assert obj.kind == "Architecture Decision Record"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_755(tampered)
    try:
        build_755("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.55 Architecture Decision Record")

if __name__ == "__main__": main()
