from services.phase7_785_responsive_qa_plan import build_785, valid_785

def main():
    obj=build_785("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_785(obj)
    assert obj.setup == "7.85"
    assert obj.kind == "Responsive QA Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_785(tampered)
    try:
        build_785("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.85 Responsive QA Plan")

if __name__ == "__main__": main()
