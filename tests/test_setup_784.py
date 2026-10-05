from services.phase7_784_ui_qa_plan import build_784, valid_784

def main():
    obj=build_784("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_784(obj)
    assert obj.setup == "7.84"
    assert obj.kind == "UI QA Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_784(tampered)
    try:
        build_784("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.84 UI QA Plan")

if __name__ == "__main__": main()
