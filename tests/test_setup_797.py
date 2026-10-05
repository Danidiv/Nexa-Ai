from services.phase7_797_product_quality_verification import build_797, valid_797

def main():
    obj=build_797("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_797(obj)
    assert obj.setup == "7.97"
    assert obj.kind == "Product Quality Verification"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_797(tampered)
    try:
        build_797("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.97 Product Quality Verification")

if __name__ == "__main__": main()
