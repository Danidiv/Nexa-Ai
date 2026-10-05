from services.phase7_765_api_generation_plan import build_765, valid_765

def main():
    obj=build_765("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_765(obj)
    assert obj.setup == "7.65"
    assert obj.kind == "API Generation Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_765(tampered)
    try:
        build_765("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.65 API Generation Plan")

if __name__ == "__main__": main()
