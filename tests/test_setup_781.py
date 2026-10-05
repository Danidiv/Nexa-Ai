from services.phase7_781_functional_qa_plan import build_781, valid_781

def main():
    obj=build_781("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_781(obj)
    assert obj.setup == "7.81"
    assert obj.kind == "Functional QA Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_781(tampered)
    try:
        build_781("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.81 Functional QA Plan")

if __name__ == "__main__": main()
