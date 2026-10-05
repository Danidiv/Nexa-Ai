from services.phase7_800_integrated_lovable_level_product_builder_v2 import build_800, valid_800

def main():
    obj=build_800("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_800(obj)
    assert obj.setup == "8.00"
    assert obj.kind == "Integrated Lovable-Level Product Builder V2"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_800(tampered)
    try:
        build_800("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.00 Integrated Lovable-Level Product Builder V2")

if __name__ == "__main__": main()
