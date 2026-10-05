from services.phase7_760_unified_product_context import build_760, valid_760

def main():
    obj=build_760("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_760(obj)
    assert obj.setup == "7.60"
    assert obj.kind == "Unified Product Context"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_760(tampered)
    try:
        build_760("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.60 Unified Product Context")

if __name__ == "__main__": main()
