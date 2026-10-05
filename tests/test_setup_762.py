from services.phase7_762_component_generation_plan import build_762, valid_762

def main():
    obj=build_762("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_762(obj)
    assert obj.setup == "7.62"
    assert obj.kind == "Component Generation Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_762(tampered)
    try:
        build_762("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.62 Component Generation Plan")

if __name__ == "__main__": main()
