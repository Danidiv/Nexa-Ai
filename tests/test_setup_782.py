from services.phase7_782_api_qa_plan import build_782, valid_782

def main():
    obj=build_782("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_782(obj)
    assert obj.setup == "7.82"
    assert obj.kind == "API QA Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_782(tampered)
    try:
        build_782("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.82 API QA Plan")

if __name__ == "__main__": main()
