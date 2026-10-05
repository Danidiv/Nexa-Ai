from services.phase7_789_regression_qa_plan import build_789, valid_789

def main():
    obj=build_789("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_789(obj)
    assert obj.setup == "7.89"
    assert obj.kind == "Regression QA Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_789(tampered)
    try:
        build_789("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.89 Regression QA Plan")

if __name__ == "__main__": main()
