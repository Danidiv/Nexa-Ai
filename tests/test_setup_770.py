from services.phase7_770_autonomous_product_implementation_plan import build_770, valid_770

def main():
    obj=build_770("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_770(obj)
    assert obj.setup == "7.70"
    assert obj.kind == "Autonomous Product Implementation Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_770(tampered)
    try:
        build_770("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.70 Autonomous Product Implementation Plan")

if __name__ == "__main__": main()
