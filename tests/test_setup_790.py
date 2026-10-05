from services.phase7_790_autonomous_product_qa_record import build_790, valid_790

def main():
    obj=build_790("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_790(obj)
    assert obj.setup == "7.90"
    assert obj.kind == "Autonomous Product QA Record"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_790(tampered)
    try:
        build_790("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.90 Autonomous Product QA Record")

if __name__ == "__main__": main()
