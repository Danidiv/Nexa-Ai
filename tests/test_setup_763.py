from services.phase7_763_page_generation_plan import build_763, valid_763

def main():
    obj=build_763("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_763(obj)
    assert obj.setup == "7.63"
    assert obj.kind == "Page Generation Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_763(tampered)
    try:
        build_763("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.63 Page Generation Plan")

if __name__ == "__main__": main()
