from services.phase7_754_product_scope_boundary import build_754, valid_754

def main():
    obj=build_754("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_754(obj)
    assert obj.setup == "7.54"
    assert obj.kind == "Product Scope Boundary"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_754(tampered)
    try:
        build_754("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.54 Product Scope Boundary")

if __name__ == "__main__": main()
