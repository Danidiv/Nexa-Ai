from services.phase7_786_accessibility_qa_plan import build_786, valid_786

def main():
    obj=build_786("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_786(obj)
    assert obj.setup == "7.86"
    assert obj.kind == "Accessibility QA Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_786(tampered)
    try:
        build_786("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.86 Accessibility QA Plan")

if __name__ == "__main__": main()
