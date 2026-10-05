from services.phase7_787_performance_qa_plan import build_787, valid_787

def main():
    obj=build_787("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_787(obj)
    assert obj.setup == "7.87"
    assert obj.kind == "Performance QA Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_787(tampered)
    try:
        build_787("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.87 Performance QA Plan")

if __name__ == "__main__": main()
