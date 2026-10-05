from services.phase7_788_security_qa_plan import build_788, valid_788

def main():
    obj=build_788("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_788(obj)
    assert obj.setup == "7.88"
    assert obj.kind == "Security QA Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_788(tampered)
    try:
        build_788("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.88 Security QA Plan")

if __name__ == "__main__": main()
