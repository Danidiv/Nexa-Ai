from services.phase7_761_ui_generation_plan import build_761, valid_761

def main():
    obj=build_761("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_761(obj)
    assert obj.setup == "7.61"
    assert obj.kind == "UI Generation Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_761(tampered)
    try:
        build_761("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.61 UI Generation Plan")

if __name__ == "__main__": main()
